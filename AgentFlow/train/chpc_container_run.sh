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
# NCCL upgrade: inject libnccl.so.2 >= 2.26.2 to fix Blackwell shared-memory
# kernel launch failure.
#
# The container ships NCCL 2.25.1, which has a confirmed bug on Blackwell GPUs
# (sm_120): NCCL's collective kernels request more shared memory than Blackwell
# allows per CUDA function (82240 B requested vs 79856 B limit).  This causes
# cuLaunchKernel to return CUDA_ERROR_INVALID_ARGUMENT (1), reported as:
#   "NCCL INFO ncclMaxSharedMem 82240 exceeds device/fn maxSharedMem 79856"
#   "enqueue.cc:NNNN NCCL WARN Cuda failure 1 'invalid argument'"
# The bug was fixed in NCCL 2.26.2 (release notes: "Fixed shared memory usage
# on recent Blackwell GPUs").
#
# We download the nvidia-nccl-cu12==2.26.2 PyPI wheel (a zip file) to scratch
# and unpack only the lib/ directory.  The 2.26.2 libnccl.so.2 is then
# bind-mounted directly over /lib/x86_64-linux-gnu/libnccl.so.2 — the exact
# path confirmed by `ldd libtorch_cuda.so` inside the NGC 25.02 container.
# LD_LIBRARY_PATH injection is not used because --nv re-injects the container's
# own library paths after environment setup, overriding LD_LIBRARY_PATH.
#
# The wheel is ~250 MB (NCCL library with debug symbols); extraction is ~4 s.
# The result is cached under _SIF_PKGS_DIR/nccl_lib; re-extracted only if
# the marker file is absent (i.e. first run or after rm -rf _SIF_PKGS_DIR).
# ---------------------------------------------------------------------------
_NCCL_LIB_DIR="${_SIF_PKGS_DIR}/nccl_lib"
_NCCL_MARKER="${_NCCL_LIB_DIR}/.nccl_extracted"
_NCCL_WHEEL_URL="https://files.pythonhosted.org/packages/67/ca/f42388aed0fddd64ade7493dbba36e1f534d4e6fdbdd355c6a90030ae028/nvidia_nccl_cu12-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl"
_NCCL_WHEEL_CACHE="${_SIF_PKGS_DIR}/nvidia_nccl_cu12-2.26.2.whl"

if [[ ! -f "${_NCCL_MARKER}" ]]; then
  echo "NCCL 2.25.1 (container) has a Blackwell shared-memory bug fixed in 2.26.2."
  echo "Downloading nvidia-nccl-cu12==2.26.2 wheel (~250 MB) to scratch ..."
  mkdir -p "${_NCCL_LIB_DIR}"
  if command -v curl &>/dev/null; then
    curl -fsSL -o "${_NCCL_WHEEL_CACHE}" "${_NCCL_WHEEL_URL}"
  else
    wget -q -O "${_NCCL_WHEEL_CACHE}" "${_NCCL_WHEEL_URL}"
  fi
  echo "Extracting libnccl.so from wheel ..."
  # The wheel (a zip archive) stores the library as nvidia/nccl/lib/libnccl.so.2
  # (no version suffix in this PyPI wheel — the SONAME is the filename).
  unzip -q -o "${_NCCL_WHEEL_CACHE}" "nvidia/nccl/lib/*" -d "${_NCCL_LIB_DIR}"
  rm -f "${_NCCL_WHEEL_CACHE}"
  touch "${_NCCL_MARKER}"
  echo "  Done. NCCL 2.26.2 cached at ${_NCCL_LIB_DIR}"
fi

# The .so inside the wheel is named libnccl.so.2 (SONAME = filename; no extra
# version suffix).  Use it directly as the bind-mount source.
_NCCL_SO="${_NCCL_LIB_DIR}/nvidia/nccl/lib/libnccl.so.2"
if [[ ! -f "${_NCCL_SO}" ]]; then
  echo "WARNING: ${_NCCL_SO} not found after extraction — NCCL injection will not work." >&2
  _NCCL_BIND_ARGS=""
else
  echo "NCCL bind-mount source: ${_NCCL_SO}"
  # In the NGC 25.02 container libtorch_cuda.so's RUNPATH is:
  #   $ORIGIN:/lib/intel64:...:/usr/local/cuda/lib64
  # ldd resolves libnccl.so.2 to: /lib/x86_64-linux-gnu/libnccl.so.2
  # That is the one and only path we must bind-mount over.
  # The pip install paths (nvidia/nccl/lib, torch/lib) are NOT in the RUNPATH
  # and were never consulted — which is why all previous bind attempts failed.
  #
  # We bind unconditionally over the confirmed path (no apptainer probe needed;
  # Apptainer silently ignores bind-mounts over non-existent target paths).
  # /lib/x86_64-linux-gnu/libnccl.so.2 is a symlink → libnccl.so.2.25.1.
  # Apptainer cannot bind-mount over a symlink; the dynamic linker follows
  # the symlink and loads the versioned file directly.  We must bind-mount
  # over the symlink TARGET (the versioned filename) to intercept the load.
  _NCCL_VERSIONED_TARGET=""
  _nccl_link=$(apptainer exec "${IMAGE}" readlink /lib/x86_64-linux-gnu/libnccl.so.2 2>/dev/null || true)
  if [[ -n "${_nccl_link}" ]]; then
    # readlink returns just the filename (e.g. libnccl.so.2.25.1); prepend dir.
    _NCCL_VERSIONED_TARGET="/lib/x86_64-linux-gnu/${_nccl_link}"
  else
    # Fallback: not a symlink, bind over the path directly.
    _NCCL_VERSIONED_TARGET="/lib/x86_64-linux-gnu/libnccl.so.2"
  fi
  _NCCL_BIND_ARGS="--bind ${_NCCL_SO}:${_NCCL_VERSIONED_TARGET}"
  echo "  Will bind-mount over: ${_NCCL_VERSIONED_TARGET}"
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
#                               cudaIpcGetMemHandle fails with "invalid argument"
#                               on this node.  P2P is disabled so NCCL uses SHM.
# NCCL_SHM_DISABLE is intentionally NOT set.  SHM (POSIX shared-memory staging)
#                               keeps nNodes=1 and localRanks=2.  Setting
#                               NCCL_SHM_DISABLE=1 forces nNodes=2 (NCCL classifies
#                               the two processes as separate nodes), which leaves
#                               no valid intra-node transport and causes
#                               "No transport found" errors.
# NCCL_P2P_DIRECT_DISABLE=1  : forbid NCCL from directly accessing user GPU
#                               buffers across processes via CUDA IPC/peer access.
#                               Without this, NCCL's SHM transport uses the
#                               "direct" submode (logged as "SHM/direct/direct"),
#                               which calls cudaMemcpyPeerAsync to copy data
#                               directly between GPU contexts across processes.
#                               Apptainer blocks cross-process CUDA peer access,
#                               causing a silent CUDA context corruption during
#                               ncclCommInitRank that surfaces as "illegal memory
#                               access" at the next CUDA API call after Init COMPLETE.
#                               With NCCL_P2P_DIRECT_DISABLE=1 NCCL falls back to
#                               the host-copy SHM submode, staging data through
#                               /dev/shm CPU-side buffers — fully supported in any
#                               container environment.
# NCCL_SOCKET_IFNAME=lo      : force all ranks to use the loopback interface
#                               for bootstrap and data.  Without this, different
#                               worker processes may resolve to different network
#                               interfaces causing NCCL to count distinct IPs as
#                               distinct nodes.
# UCX_TLS=tcp,self            : restrict any residual UCX init to TCP loopback.
#
# NOTE: NCCL_CUMEM_HOST_ENABLE is intentionally NOT set.
# With NCCL 2.25.1 we needed NCCL_CUMEM_HOST_ENABLE=0 to prevent
# "Cuda failure 1 'invalid argument'" in the SHM transport (cuMemCreate
# for SHM host buffers failed inside Apptainer).  NCCL 2.26.2 fixes the
# Blackwell shared-memory kernel size bug that caused that crash.  Keeping
# NCCL_CUMEM_HOST_ENABLE=0 with 2.26.2 instead causes
# "CUDA error: an illegal memory access" in ncclCommWatchdog during
# FSDP init_model, because the SHM direct path requires cuMem-backed
# buffers to be addressable across processes.
#
# NCCL_CUMEM_ENABLE=1 is set explicitly below to override CHPC's host
# environment which injects NCCL_CUMEM_ENABLE=0 via its RDMA/HPC plugin.
# NCCL 2.26.2 on Blackwell requires VMM (cuMemCreate) for communicator
# scratch buffers even on the intra-node SHM path; without it the CUDA
# context on rank 1 becomes corrupted after Init COMPLETE.
export NCCL_IB_DISABLE=1
export UCX_TLS=tcp,self
export NCCL_IGNORE_DISABLED_P2P=1
export NCCL_P2P_DISABLE=1
export NCCL_P2P_DIRECT_DISABLE=1
export NCCL_SOCKET_IFNAME=lo
# NCCL_CUMEM_ENABLE=1: explicitly override the CHPC host environment, which
# injects NCCL_CUMEM_ENABLE=0 via the RDMA plugin.  NCCL 2.26.2 on Blackwell
# (sm_120) requires CUDA VMM (cuMemCreate) for its internal communicator
# scratch buffers even on the intra-node SHM path.  With =0 those allocations
# fail silently during ncclCommInitRank, leaving the CUDA context on rank 1 in
# a partially initialized state.  The corruption surfaces immediately after
# Init COMPLETE as "illegal memory access" in torch.cuda.empty_cache() and
# param.to(device).  Setting =1 restores the default VMM-enabled behavior.
export NCCL_CUMEM_ENABLE=1
# Force all NCCL ranks to report the same host identity.
# Apptainer may give each worker process a different UTS namespace (hostname),
# causing NCCL's getHostHash() to return different values per process even on
# the same physical node.  NCCL uses host hashes to determine nNodes: if two
# ranks hash differently it concludes nNodes=2 (multi-node) and uses a network
# proxy path that fails with "Cuda failure 1 'invalid argument'".
# Setting NCCL_HOSTID to a fixed string forces all ranks on this job to share
# the same host identity → nNodes=1 → intra-node transport → correct operation.
export NCCL_HOSTID=datamorphernode0
# Ray uses fractional GPU allocation (num_gpus=1/3 per colocated actor).
# For fractional allocations Ray does NOT set CUDA_VISIBLE_DEVICES — that only
# happens for whole-GPU actors.  We do NOT set CUDA_VISIBLE_DEVICES either:
# NCCL uses physical GPU indices internally, so remapping via CUDA_VISIBLE_DEVICES
# causes cudaSetDevice(1) to fail with "invalid argument" when only one device
# is visible.  Instead, the _patched_init_process_group hook in entrypoint.py
# calls torch.cuda.set_device(LOCAL_RANK) just before init_process_group so
# all CUDA allocations land on the correct GPU without restricting visibility.
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
# vLLM v1's EngineCore runs in a spawned subprocess.  That subprocess queries
# the actual free GPU memory at startup — and sees near-zero free memory
# because the FSDP WorkerDict is already fully loaded (~65 GiB on GPU 0).
# vLLM v1 then computes available_memory = min(free_mem, utilization×total)
# and finds nothing left for even a single KV cache block → crashes.
#
# vLLM v0 uses CuMemAllocator (VMM) for both weights and KV cache.  VMM
# reservations are virtual — they don't require physical GPU pages at
# reservation time.  The physical pages are only faulted in when the pages
# are first accessed (i.e. during wake_up(), after FSDP has offloaded to CPU
# and freed the physical pages).  This is the intended flow for colocated
# FSDP + vLLM training in veRL.
export VLLM_USE_V1=0

echo "Running container sanity imports ..."
# shellcheck disable=SC2086
apptainer exec --nv \
  --bind "${REPO_ROOT}:/workspace/transschema" \
  --bind "/scratch/general/vast/u1592362:/scratch/general/vast/u1592362" \
  ${_NCCL_BIND_ARGS} \
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
# ldd confirms libtorch_cuda.so resolves libnccl.so.2 via symlink to
# /lib/x86_64-linux-gnu/libnccl.so.2.25.1 (versioned target).
# We must load the versioned file directly to check the injected version.
import glob as _glob
_NCCL_VERSIONED = ""
for _candidate in _glob.glob("/lib/x86_64-linux-gnu/libnccl.so.2.*"):
    _NCCL_VERSIONED = _candidate
    break
if not _NCCL_VERSIONED:
    _NCCL_VERSIONED = "/lib/x86_64-linux-gnu/libnccl.so.2"
try:
    _lib = ctypes.CDLL(_NCCL_VERSIONED)
    _ver = ctypes.c_int(0)
    _lib.ncclGetVersion(ctypes.byref(_ver))
    _v = _ver.value
    _vs = f"{_v // 10000}.{(_v % 10000) // 100}.{_v % 100}"
    print(f"  NCCL version at {_NCCL_VERSIONED}: {_vs}")
    if _v < 22602:
        print(f"  ERROR: NCCL {_vs} < 2.26.2 — Blackwell shared-memory bug not fixed!")
        print( "         Check that the NCCL bind-mounts succeeded.")
        import sys; sys.exit(4)
    else:
        print(f"  OK NCCL >= 2.26.2 confirmed")
except Exception as e:
    print(f"  WARNING: could not query NCCL version from {_NCCL_VERSIONED}: {e}")
PY

# shellcheck disable=SC2086
exec apptainer exec --nv \
  --bind "${REPO_ROOT}:/workspace/transschema" \
  --bind "/scratch/general/vast/u1592362:/scratch/general/vast/u1592362" \
  ${_NCCL_BIND_ARGS} \
  --pwd /workspace/transschema/AgentFlow \
  "${IMAGE}" \
  "${PYTHON_IN_CONTAINER}" train/train_datamorpheragent.py --skip_dep_check "$@"

