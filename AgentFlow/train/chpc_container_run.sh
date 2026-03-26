#!/usr/bin/env bash
# Run DataMorpher training inside an Apptainer container on CHPC.
# Usage:
#   APPTAINER_IMAGE=/path/to/transschema-agentflow-cu128.sif \
#     bash train/chpc_container_run.sh --smoke_test

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTFLOW_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${AGENTFLOW_ROOT}/.." && pwd)"

IMAGE="${APPTAINER_IMAGE:-}"
if [[ -z "${IMAGE}" ]]; then
  echo "ERROR: set APPTAINER_IMAGE to a .sif built from AgentFlow/container/apptainer.def" >&2
  exit 2
fi

if [[ ! -f "${IMAGE}" ]]; then
  echo "ERROR: container image not found: ${IMAGE}" >&2
  exit 2
fi

mkdir -p /scratch/general/vast/u1592362/hf_cache
mkdir -p /scratch/general/vast/u1592362/AgentFlow_Checkpoints
mkdir -p /scratch/general/vast/u1592362/AgentFlow_Rollouts

# ---------------------------------------------------------------------------
# Squashfuse-bypass: extract packages to scratch.
#
# Apptainer mounts SIF images via squashfuse_ll (a user-space FUSE daemon).
# squashfuse_ll handles one kernel FUSE request at a time through a single
# /dev/fuse fd.  When AgentFlow's Trainer loads tools in parallel it spawns
# N independent Python processes that each try to open vllm/__init__.py and
# openai/__init__.py from squashfuse_ll concurrently.  The FUSE daemon
# becomes overloaded and closes the fd, returning ENOTCONN to every reader.
#
# Fix: copy the two problematic packages to a real filesystem (VAST scratch)
# once.  PYTHONPATH is then prepended with that directory so every Python
# process — spawned or forked, regardless of concurrency — finds these
# packages without ever touching squashfuse_ll.
#
# The copy is keyed to the SIF's mtime; it is automatically redone when
# the container image is rebuilt, otherwise it is instantaneous.
# ---------------------------------------------------------------------------
_SIF_PKGS_DIR="/scratch/general/vast/u1592362/AgentFlow_sif_pkgs"
_SIF_PKGS_MARKER="${_SIF_PKGS_DIR}/.extracted_from_sif"
_need_extract=false
if [[ ! -f "${_SIF_PKGS_MARKER}" ]]; then
  _need_extract=true
elif [[ "${IMAGE}" -nt "${_SIF_PKGS_MARKER}" ]]; then
  echo "SIF image is newer than cached packages; re-extracting..."
  _need_extract=true
fi

if [[ "${_need_extract}" == "true" ]]; then
  echo "Extracting Python packages from SIF to scratch (avoids squashfuse_ll"
  echo "  concurrency failures during parallel tool loading)."
  echo "  This runs once; subsequent launches are instant."
  rm -rf "${_SIF_PKGS_DIR}"
  mkdir -p "${_SIF_PKGS_DIR}"
  # Use -rL so symlinks inside the container are dereferenced; all files land on scratch.
  # Shell glob expansion happens inside the container via /bin/sh -c.
  apptainer exec \
    --bind "/scratch/general/vast/u1592362:/scratch/general/vast/u1592362" \
    "${IMAGE}" \
    /bin/sh -c "
      set -e
      DEST=\"${_SIF_PKGS_DIR}\"
      SP=/usr/local/lib/python3.12/dist-packages
      cp -rL \"\${SP}/vllm\"   \"\${DEST}/\"
      cp -rL \"\${SP}/openai\" \"\${DEST}/\"
      for d in \"\${SP}\"/vllm-*.dist-info \"\${SP}\"/openai-*.dist-info; do
        [ -d \"\${d}\" ] && cp -rL \"\${d}\" \"\${DEST}/\"
      done
    "
  touch "${_SIF_PKGS_MARKER}"
  echo "  Done. Packages cached at ${_SIF_PKGS_DIR}"
fi
export PYTHONPATH="${_SIF_PKGS_DIR}:${PYTHONPATH:-}"

# ---------------------------------------------------------------------------
# NCCL upgrade: download libnccl.so.2 >= 2.26.2 to fix Blackwell shared-memory
# kernel launch failure.
#
# The container ships NCCL 2.25.1 at /lib/x86_64-linux-gnu/libnccl.so.2 (the
# system apt-installed path that libtorch_cuda.so resolves via RUNPATH).
# NCCL 2.25.1 has a confirmed Blackwell (sm_120) bug: collective kernels request
# 82240 B of shared memory but Blackwell caps CUDA functions at 79856 B, causing:
#   "NCCL WARN Cuda failure 1 'invalid argument'"
# Fixed in NCCL 2.26.2.
#
# Strategy:
#   1. Check the container's pip-installed NCCL at
#      /usr/local/lib/python3.12/dist-packages/nvidia/nccl/lib/libnccl.so.2
#      NGC 25.02 ships a newer NCCL there; if >= 2.26.2 use it directly.
#   2. If not available or too old, try downloading the PyPI wheel.
#   3. Inject via LD_PRELOAD from /dev/shm (RAM-backed, never NFS-stale).
#
# _NCCL_LIB_DIR is intentionally placed OUTSIDE _SIF_PKGS_DIR so that
# rm -rf _SIF_PKGS_DIR (triggered on SIF image update) does not wipe the
# downloaded NCCL library.
# ---------------------------------------------------------------------------
_NCCL_LIB_DIR="/scratch/general/vast/u1592362/AgentFlow_nccl_lib"
_NCCL_MARKER="${_NCCL_LIB_DIR}/.nccl_extracted"
_NCCL_WHEEL_URL="https://files.pythonhosted.org/packages/67/ca/f42388aed0fddd64ade7493dbba36e1f534d4e6fdbdd355c6a90030ae028/nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl"
_NCCL_WHEEL_CACHE="${_NCCL_LIB_DIR}/nvidia_nccl_cu12-2.26.2.whl"

if [[ ! -f "${_NCCL_MARKER}" ]]; then
  mkdir -p "${_NCCL_LIB_DIR}"

  # Strategy 1: check the container's pip-installed NCCL (often >= 2.26.2 in NGC 25.02).
  _CONTAINER_NCCL="/usr/local/lib/python3.12/dist-packages/nvidia/nccl/lib/libnccl.so.2"

  _container_nccl_ver=$(apptainer exec "${IMAGE}" /bin/sh -c \
    "python3 -c \"
import ctypes, sys
try:
    lib = ctypes.CDLL('${_CONTAINER_NCCL}')
    v = ctypes.c_int(0)
    lib.ncclGetVersion(ctypes.byref(v))
    sys.stdout.write(str(v.value))
except Exception:
    sys.stdout.write('0')
\"" 2>/dev/null || echo 0)

  if [[ "${_container_nccl_ver}" -ge 22602 ]] 2>/dev/null; then
    echo "Container pip NCCL version ${_container_nccl_ver} >= 2.26.2; extracting from container ..."
    apptainer exec \
      --bind "/scratch/general/vast/u1592362:/scratch/general/vast/u1592362" \
      "${IMAGE}" \
      /bin/sh -c "cp -L '${_CONTAINER_NCCL}' '${_NCCL_LIB_DIR}/libnccl.so.2'"
    touch "${_NCCL_MARKER}"
    echo "  Done. NCCL extracted from container at ${_NCCL_LIB_DIR}/libnccl.so.2"
  else
    # Strategy 2: download from PyPI.
    echo "NCCL 2.25.1 (container) has a Blackwell shared-memory bug fixed in 2.26.2."
    echo "Downloading nvidia-nccl-cu12==2.26.2 wheel (~250 MB) to scratch ..."
    _download_ok=false
    if command -v curl &>/dev/null; then
      curl -fsSL --connect-timeout 30 -o "${_NCCL_WHEEL_CACHE}" "${_NCCL_WHEEL_URL}" \
        && _download_ok=true || true
    fi
    if [[ "${_download_ok}" == "false" ]] && command -v wget &>/dev/null; then
      wget -q --timeout=30 -O "${_NCCL_WHEEL_CACHE}" "${_NCCL_WHEEL_URL}" \
        && _download_ok=true || true
    fi
    if [[ "${_download_ok}" == "true" ]] && [[ -s "${_NCCL_WHEEL_CACHE}" ]]; then
      echo "Extracting libnccl.so from wheel ..."
      mkdir -p "${_NCCL_LIB_DIR}/wheel_extract"
      unzip -q -o "${_NCCL_WHEEL_CACHE}" "nvidia/nccl/lib/libnccl.so.2" \
        -d "${_NCCL_LIB_DIR}/wheel_extract"
      _wheel_so="${_NCCL_LIB_DIR}/wheel_extract/nvidia/nccl/lib/libnccl.so.2"
      if [[ -f "${_wheel_so}" ]]; then
        cp -f "${_wheel_so}" "${_NCCL_LIB_DIR}/libnccl.so.2"
        rm -rf "${_NCCL_LIB_DIR}/wheel_extract"
        rm -f "${_NCCL_WHEEL_CACHE}"
        touch "${_NCCL_MARKER}"
        echo "  Done. NCCL 2.26.2 downloaded and cached at ${_NCCL_LIB_DIR}/libnccl.so.2"
      else
        echo "WARNING: wheel extraction yielded no libnccl.so.2; NCCL injection will not work." >&2
      fi
    else
      echo "WARNING: NCCL wheel download failed (no internet access?); NCCL injection will not work." >&2
      echo "         To fix: on a machine with internet access, run:" >&2
      echo "           mkdir -p ${_NCCL_LIB_DIR}" >&2
      echo "           wget -O ${_NCCL_LIB_DIR}/libnccl.so.2 <url>" >&2
      echo "           touch ${_NCCL_MARKER}" >&2
    fi
  fi
fi

# ---------------------------------------------------------------------------
# NCCL injection via LD_PRELOAD from /dev/shm (RAM-backed, never stale).
#
# Why not bind-mount: Apptainer bind-mounts capture the file's inode at
# container-start time.  On VAST NFS scratch, if the inode is ever evicted
# or replaced (e.g. after rm -rf + re-extraction), running workers that
# already have the bind-mount open get ESTALE ("Stale file handle") the next
# time they try to read the library.  This breaks torch import in Ray workers:
#   ImportError: libnccl.so.2: cannot open shared object file: Stale file handle
#
# Why LD_PRELOAD works: LD_PRELOAD with a full path is resolved once at
# process start (dlopen by the dynamic linker before any other library).
# As long as the file exists at the moment the process starts it is mapped
# into memory; subsequent NFS inode changes do not affect the already-mapped
# pages.  /dev/shm is RAM-backed (tmpfs), so reads are entirely in-kernel
# memory — ESTALE is impossible.
#
# Why LD_PRELOAD overrides the container's NCCL: LD_PRELOAD is processed
# before LD_LIBRARY_PATH and before any RUNPATH/RPATH embedded in binaries.
# The preloaded libnccl.so.2 satisfies the SONAME dependency before the
# linker ever searches /lib/x86_64-linux-gnu/libnccl.so.2.25.1.
# Apptainer's --nv flag only prepends CUDA driver/toolkit paths to
# LD_LIBRARY_PATH; it does not reset or override LD_PRELOAD.
# ---------------------------------------------------------------------------
_NCCL_SO="${_NCCL_LIB_DIR}/libnccl.so.2"
_NCCL_SHM="/dev/shm/libnccl_2262.so.2"   # fixed name; safe to overwrite each run
if [[ ! -f "${_NCCL_SO}" ]]; then
  echo "WARNING: ${_NCCL_SO} not found after extraction — NCCL injection will not work." >&2
else
  echo "Copying NCCL 2.26.2 to /dev/shm for stale-NFS-safe LD_PRELOAD injection ..."
  cp -f "${_NCCL_SO}" "${_NCCL_SHM}"
  chmod 755 "${_NCCL_SHM}"
  echo "  NCCL LD_PRELOAD source: ${_NCCL_SHM}"
  export LD_PRELOAD="${_NCCL_SHM}${LD_PRELOAD:+:${LD_PRELOAD}}"
fi

# ---------------------------------------------------------------------------
# Patch vLLM cumem_allocator: flush PyTorch cache before wake_up.
#
# FSDPVLLMShardingManager.__enter__ collects the FSDP state dict before
# calling inference_engine.wake_up().  The state_dict call allocates GPU
# tensors via cudaMalloc.  PyTorch's CUDA allocator caches these freed
# blocks instead of returning them to the CUDA driver.  When wake_up then
# calls cuMemCreate (to re-allocate physical pages for vLLM model weights)
# the driver cannot satisfy the request because the physical pages are still
# held in PyTorch's cache → CUDA_ERROR_OUT_OF_MEMORY.
#
# Fix (confirmed in verl issue #302 / verl PR #575): call
# torch.cuda.empty_cache() inside CuMemAllocator.wake_up() before each
# cuMemCreate.  empty_cache() returns PyTorch's cached pages to the CUDA
# driver, making them available for cuMemCreate.
#
# We append the monkey-patch to the scratch copy of cumem.py.  That copy
# is loaded in preference to the SIF version because _SIF_PKGS_DIR is
# first on PYTHONPATH.  The marker comment prevents re-patching on re-runs.
# ---------------------------------------------------------------------------
_CUMEM_PY="${_SIF_PKGS_DIR}/vllm/device_allocator/cumem.py"
if [[ -f "${_CUMEM_PY}" ]] && ! grep -q "PATCHED_EMPTY_CACHE_BEFORE_WAKE_UP" "${_CUMEM_PY}"; then
  cat >> "${_CUMEM_PY}" << 'CUMEM_PATCH'

# PATCHED_EMPTY_CACHE_BEFORE_WAKE_UP
# Wrap CuMemAllocator.wake_up to call torch.cuda.empty_cache() first.
# This releases PyTorch's cached CUDA blocks back to the driver so that
# cuMemCreate can obtain physical GPU pages for the vLLM model weights.
_orig_cumem_wake_up = CuMemAllocator.wake_up
def _patched_cumem_wake_up(self, tags=None):
    import torch
    torch.cuda.empty_cache()
    _orig_cumem_wake_up(self, tags)
CuMemAllocator.wake_up = _patched_cumem_wake_up
CUMEM_PATCH
  echo "  Patched ${_CUMEM_PY}: torch.cuda.empty_cache() added before cuMemCreate."
fi


unset ROCR_VISIBLE_DEVICES
# Do NOT export CUDA_VISIBLE_DEVICES here.  Ray manages per-worker GPU
# assignment via placement groups and sets CUDA_VISIBLE_DEVICES per actor.
# Exporting a multi-GPU value (e.g. "0,1") causes all workers to see the
# same devices, leading to NCCL "Duplicate GPU detected" errors.
# If SLURM or the user's environment already set CUDA_VISIBLE_DEVICES to
# restrict which physical GPUs are visible, that is fine — Ray will
# sub-assign from whatever is visible.  We just don't override it here.
unset CUDA_VISIBLE_DEVICES 2>/dev/null || true
export HF_HOME="${HF_HOME:-/scratch/general/vast/u1592362/hf_cache}"
export PYTHONPATH="${REPO_ROOT}:${AGENTFLOW_ROOT}:${AGENTFLOW_ROOT}/train${PYTHONPATH:+:${PYTHONPATH}}"
RUNTIME_VENV="${AGENTFLOW_RUNTIME_VENV:-/scratch/general/vast/u1592362/AgentFlow_runtime_venv_current}"
LEGACY_RUNTIME_VENV="/scratch/general/vast/u1592362/AgentFlow_runtime_venv"
PYTHON_IN_CONTAINER="python"

runtime_site_packages_dir() {
  local venv_path="$1"
  local match
  for match in "${venv_path}"/lib/python*/site-packages; do
    if [[ -d "${match}" ]]; then
      printf '%s\n' "${match}"
      return 0
    fi
  done
  return 1
}

if [[ -x "${RUNTIME_VENV}/bin/python" ]]; then
  PYTHON_IN_CONTAINER="${RUNTIME_VENV}/bin/python"
  echo "Using scratch runtime env: ${RUNTIME_VENV}"
  if RUNTIME_SITE_PACKAGES="$(runtime_site_packages_dir "${RUNTIME_VENV}")"; then
    # _SIF_PKGS_DIR must stay first so sitecustomize.py is found before venv packages.
    export PYTHONPATH="${_SIF_PKGS_DIR}:${RUNTIME_SITE_PACKAGES}:${PYTHONPATH}"
    echo "Injected runtime site-packages into PYTHONPATH for Ray workers."
  fi
elif [[ -x "${LEGACY_RUNTIME_VENV}/bin/python" ]]; then
  PYTHON_IN_CONTAINER="${LEGACY_RUNTIME_VENV}/bin/python"
  echo "Using legacy scratch runtime env: ${LEGACY_RUNTIME_VENV}"
  if LEGACY_RUNTIME_SITE_PACKAGES="$(runtime_site_packages_dir "${LEGACY_RUNTIME_VENV}")"; then
    # _SIF_PKGS_DIR must stay first so sitecustomize.py is found before venv packages.
    export PYTHONPATH="${_SIF_PKGS_DIR}:${LEGACY_RUNTIME_SITE_PACKAGES}:${PYTHONPATH}"
    echo "Injected legacy runtime site-packages into PYTHONPATH for Ray workers."
  fi
else
  echo "No scratch runtime env found at ${RUNTIME_VENV}."
  echo "For lightweight Python dependency updates without rebuilding the SIF, run:"
  echo "  APPTAINER_IMAGE=${IMAGE} bash AgentFlow/train/chpc_bootstrap_env.sh"
fi

# Ensure Ray worker processes use the same Python interpreter as the launcher.
# Without this, Ray can default to system python, which may miss runtime-only deps.
export RAY_PYTHON_EXECUTABLE="${PYTHON_IN_CONTAINER}"
echo "RAY_PYTHON_EXECUTABLE=${RAY_PYTHON_EXECUTABLE}"

# Avoid wandb login failures on batch/cluster runs unless the user explicitly configured it.
if [[ -z "${WANDB_API_KEY:-}" && -z "${WANDB_MODE:-}" ]]; then
  export WANDB_MODE=offline
fi

# Disable Ray's task-event telemetry flush on actor shutdown.
# Without this, the vLLM rollout-server actor races between flushing telemetry
# to the GCS (via UCX) and the GCS connection being torn down, producing a
# harmless but noisy SIGSEGV in ray::gcs::TaskInfoAccessor::AsyncAddTaskEventData.
# Setting this to 0 disables the periodic flush; task events are never sent.
export RAY_task_events_report_interval_ms=0

# Force NCCL to use TCP sockets instead of InfiniBand / UCX, and work
# around PCIe bridge device-ID collision on this Blackwell workstation.
#
# On CHPC nodes HPC-X (the host's OpenMPI + UCX distribution) is installed at
# /opt/hpcx/.  When NCCL initialises inside an Apptainer container it probes
# for IB devices and loads UCX's IB transport (libucs.so from HPC-X).  That
# transport crashes with SIGSEGV in ucs_handle_error when the IB device is not
# fully accessible from the container namespace.
#
# Additionally, on this node both Blackwell GPUs sit behind the same PCIe
# bridge and expose the same PCI bus ID (0x21000) to the driver.  NCCL uses
# PCI bus IDs as unique device fingerprints and therefore reports
# "Duplicate GPU detected: rank 0 and rank 1 both on CUDA device 21000".
#
# NCCL_IB_DISABLE=1          : skip InfiniBand entirely; use intra-node transports.
# NCCL_IGNORE_DISABLED_P2P=1 : ignore PCI bus-ID uniqueness checks.
#                               Both Blackwell GPUs on this node share the same
#                               PCIe bridge and expose the same bus ID (0x21000).
#                               Without this flag NCCL reports "Duplicate GPU
#                               detected" and aborts.
# NCCL_P2P_DISABLE=1         : disable direct GPU-to-GPU P2P/IPC memory copies.
#                               The Blackwell PCIe bridge bus-ID collision means
#                               cudaIpcGetMemHandle fails with "invalid argument".
# NCCL_P2P_DIRECT_DISABLE=1  : forbid direct cross-process CUDA peer access.
# NCCL_SHM_DISABLE=1         : disable SHM transport (see export block below).
# NCCL_SOCKET_IFNAME=lo      : force all ranks to use the loopback interface.
# UCX_TLS=tcp,self            : restrict any residual UCX init to TCP loopback.
# NCCL_CUMEM_ENABLE=0         : disable cuMem VMM (busId collision on this node).
# NCCL_CUMEM_HOST_ENABLE=0    : disable cuMem host-buffer allocation.
export NCCL_IB_DISABLE=1
export UCX_TLS=tcp,self
export NCCL_IGNORE_DISABLED_P2P=1
export NCCL_P2P_DISABLE=1
export NCCL_P2P_DIRECT_DISABLE=1
export NCCL_SOCKET_IFNAME=lo
# NCCL_CUMEM_ENABLE=0 / NCCL_CUMEM_HOST_ENABLE=0: disable cuMem VMM.
# GPU 1 shares the same PCIe busId as GPU 0 on this Blackwell node; cuMemCreate
# / cuMemSetAccess may be routed incorrectly, silently corrupting GPU 1's context.
# NCCL 2.26.2 fixed the Blackwell shared-memory kernel size bug in the kernel
# code itself — cuMem is not required for correctness.  Legacy cudaMalloc and
# POSIX mmap paths work correctly.
export NCCL_CUMEM_ENABLE=0
export NCCL_CUMEM_HOST_ENABLE=0
# NCCL_SHM_DISABLE=1: disable NCCL's shared-memory transport entirely.
#
# Root cause (confirmed from NCCL 2.26.2 source + PyTorch issue #178085 on
# identical Blackwell hardware):
# ncclShmOpen() calls cudaHostRegister(hptr, size, Portable|Mapped) even in
# CE mode.  "Mapped" creates a device-visible address (dptr) in the calling
# process's CUDA context and stores it as the NCCL comm's tail/head pointers
# in the device-side channel descriptor.  NCCL init kernels then write to
# those addresses on the GPU.  Apptainer creates a separate CUDA context per
# worker process; a device pointer registered in one context is inaccessible
# from a GPU kernel in another context → "CUDA error: an illegal memory access
# was encountered" in ncclCommWatchdog (init succeeds asynchronously; the
# fault is caught later when the watchdog polls finishedGPUExecutionInternal).
# CE mode only moves the data copy; the init-kernel fault remains.
# Disabling SHM forces NCCL to use NET/Socket (TCP) transport.
export NCCL_SHM_DISABLE=1
#
# IMPORTANT: do NOT set NCCL_HOSTID to the same value for all ranks.
#
# When all ranks share the same hostHash (nNodes=1) and SHM+P2P are disabled,
# NCCL routes collectives via NET/Socket/Shared — an AF_UNIX socket.  NCCL's
# NET/Socket transport only handles AF_INET/AF_INET6 and rejects AF_UNIX:
#   "NCCL WARN ncclSocketInit: connecting to address with family 1 is
#    neither AF_INET(2) nor AF_INET6(10)"
# This triggers an internal NCCL error that appears as an illegal memory
# access caught by the watchdog (NCCL issue #2057, March 2026).
#
# The correct configuration: let each rank have a distinct hostHash (nNodes=2).
# NCCL then uses inter-node NET/Socket over TCP (NCCL_SOCKET_IFNAME=lo →
# loopback 127.0.0.1), which is valid AF_INET and has no cross-process CUDA
# mappings.  The earlier "Cuda failure 1 'invalid argument'" that previously
# required nNodes=1 was caused by NCCL_CUMEM_ENABLE being unset; with
# NCCL_CUMEM_ENABLE=0 (set above), the inter-node TCP path works correctly.
# Set RAY_EXPERIMENTAL_NOSET_CUDA_VISIBLE_DEVICES=1 so all Ray workers see
# all physical GPUs.  veRL requests fractional GPUs per colocated worker
# (num_gpus = 1/max_colocate_count); with fractional allocation Ray cannot
# set CUDA_VISIBLE_DEVICES per-worker — it would assign both workers to GPU 0.
# With NOSET=1 Ray does not restrict per-worker GPU visibility, and veRL's
# _worker_setup_hook calls torch.cuda.set_device(local_rank) before NCCL
# init so each rank gets a distinct busId.
export RAY_EXPERIMENTAL_NOSET_CUDA_VISIBLE_DEVICES=1

# Disable torch.compile (TorchDynamo) for all FSDP training workers.
#
# veRL decorates dp_actor._forward_micro_batch with @torch.compile.  When
# torch._inductor compiles the first micro-batch it calls the Triton NVIDIA
# backend to generate PTX.  Triton's LLVM backend in NGC 25.02 does not
# recognise sm_120 (Blackwell) as a valid target processor, so when it tries
# to lower the warp-shuffle intrinsic llvm.nvvm.shfl.sync.bfly.i32 it cannot
# select an instruction and calls llvm::report_fatal_error(), which calls
# abort() → SIGABRT, killing the WorkerDict actor.
#
# TORCHDYNAMO_DISABLE=1 makes every @torch.compile decorator a no-op.  All
# veRL FSDP training code runs in standard PyTorch eager mode, which is
# fully correct and reproducible.  Eager mode is the accepted baseline for
# research; torch.compile is an optional throughput optimisation that can be
# re-enabled once Triton ships LLVM 19+ with sm_120 support.
export TORCHDYNAMO_DISABLE=1

# Force vLLM to use the v0 engine (not v1).
#
# VLLM_USE_V1: verl's PatchedvLLMServer uses AsyncLLM.from_vllm_config which
# is a v1-only API; it raises ValueError if VLLM_USE_V1=False.
# We must keep v1 enabled.  The OOM that previously required v0 is instead
# managed by keeping gpu_memory_utilization low enough that vLLM's KV cache
# fits in the free memory after FSDP param offload has released GPU pages.
# See gpu_memory_utilization in datamorpherconfig.yaml / train overrides.
export VLLM_USE_V1=1

echo "Running container sanity imports ..."
apptainer exec --nv \
  --bind "${REPO_ROOT}:/workspace/transschema" \
  --bind "/scratch/general/vast/u1592362:/scratch/general/vast/u1592362" \
  --pwd /workspace/transschema/AgentFlow \
  "${IMAGE}" \
  "${PYTHON_IN_CONTAINER}" - <<'PY'
import importlib
import sys

required = [
    "numpy",
    "pandas",
    "pyarrow",
    "datasets",
    "torch",
    "ray",
    "transformers",
    "yaml",
    "filelock",
    "setproctitle",
    "flash_attn.bert_padding",
    "agentflow",
]

failures = []
for name in required:
    try:
        importlib.import_module(name)
    except Exception as exc:
        failures.append((name, exc))

if failures:
    print("ERROR: active Python runtime is missing required imports:")
    for name, exc in failures:
        print(f"  - {name}: {exc}")
    sys.exit(3)

print("  OK core imports")

import torch
print(f"  torch={torch.__version__}  cuda={torch.version.cuda}")
if torch.cuda.is_available():
    device_count = torch.cuda.device_count()
    print(f"  GPU count: {device_count}")
    for i in range(device_count):
        props = torch.cuda.get_device_properties(i)
        print(f"    GPU {i}: {torch.cuda.get_device_name(i)} "
              f"(compute={props.major}.{props.minor}, mem={props.total_memory/1024**3:.1f}GiB)")
    if device_count < 2:
        print("  WARNING: Only 1 GPU detected. Multi-GPU training requires 2+ GPUs.")
        print("           Check your SLURM --gres=gpu request or node allocation.")
else:
    print("  WARNING: CUDA not available")

print("  OK flash_attn.bert_padding import")

import ctypes, os
# LD_PRELOAD injects libnccl.so.2 (2.26.2) before the container's NCCL.
# Load it directly from the preloaded path (already mapped by the linker).
_nccl_preload = os.environ.get("LD_PRELOAD", "").split(":")[0]
_NCCL_TO_CHECK = _nccl_preload if _nccl_preload else "/lib/x86_64-linux-gnu/libnccl.so.2"
try:
    _lib = ctypes.CDLL(_NCCL_TO_CHECK)
    _ver = ctypes.c_int(0)
    _lib.ncclGetVersion(ctypes.byref(_ver))
    _v = _ver.value
    _vs = f"{_v // 10000}.{(_v % 10000) // 100}.{_v % 100}"
    print(f"  NCCL version from {_NCCL_TO_CHECK}: {_vs}")
    if _v < 22602:
        print(f"  ERROR: NCCL {_vs} < 2.26.2 — Blackwell shared-memory bug not fixed!")
        print( "         Check that LD_PRELOAD injection succeeded.")
        import sys; sys.exit(4)
    else:
        print(f"  OK NCCL >= 2.26.2 confirmed")
except Exception as e:
    print(f"  WARNING: could not query NCCL version: {e}")
PY

exec apptainer exec --nv \
  --bind "${REPO_ROOT}:/workspace/transschema" \
  --bind "/scratch/general/vast/u1592362:/scratch/general/vast/u1592362" \
  --pwd /workspace/transschema/AgentFlow \
  "${IMAGE}" \
  "${PYTHON_IN_CONTAINER}" train/train_datamorpheragent.py --skip_dep_check "$@"

