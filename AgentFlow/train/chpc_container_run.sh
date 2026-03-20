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
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1}"
export HF_HOME="${HF_HOME:-/scratch/general/vast/u1592362/hf_cache}"
export PYTHONPATH="${REPO_ROOT}:${AGENTFLOW_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
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
    export PYTHONPATH="${RUNTIME_SITE_PACKAGES}:${PYTHONPATH}"
    echo "Injected runtime site-packages into PYTHONPATH for Ray workers."
  fi
elif [[ -x "${LEGACY_RUNTIME_VENV}/bin/python" ]]; then
  PYTHON_IN_CONTAINER="${LEGACY_RUNTIME_VENV}/bin/python"
  echo "Using legacy scratch runtime env: ${LEGACY_RUNTIME_VENV}"
  if LEGACY_RUNTIME_SITE_PACKAGES="$(runtime_site_packages_dir "${LEGACY_RUNTIME_VENV}")"; then
    export PYTHONPATH="${LEGACY_RUNTIME_SITE_PACKAGES}:${PYTHONPATH}"
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

# Force NCCL to use TCP sockets instead of InfiniBand / UCX.
#
# On CHPC nodes HPC-X (the host's OpenMPI + UCX distribution) is installed at
# /opt/hpcx/.  When NCCL initialises inside an Apptainer container it probes
# for IB devices and loads UCX's IB transport (libucs.so from HPC-X).  That
# transport crashes with SIGSEGV in ucs_handle_error when the IB device is not
# fully accessible from the container namespace.  The crash kills the colocated
# FSDP/vLLM WorkerDict actor before compute_log_prob can return results.
#
# NCCL_IB_DISABLE=1  : skip InfiniBand entirely; use socket-based transport
#                       for inter-node communication.
# NCCL_P2P_DISABLE   : NOT set.  With 2 GPUs on the same node, P2P (NVLink
#                       or PCIe) is the fastest path for FSDP all-gather /
#                       reduce-scatter.  P2P does not use UCX/IB.
# UCX_TLS=tcp,self   : in case any library still tries to init UCX, restrict
#                       it to TCP loopback only.
export NCCL_IB_DISABLE=1
export UCX_TLS=tcp,self

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

# Note: VLLM_SLEEP_LEVEL is not a recognised env var in the vLLM version
# shipped with NGC 25.02, so it has no effect here.  The cumem patch above
# (torch.cuda.empty_cache before cuMemCreate) is the operative fix.

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
    print(f"  device_capability={torch.cuda.get_device_capability()}")

print("  OK flash_attn.bert_padding import")
PY

exec apptainer exec --nv \
  --bind "${REPO_ROOT}:/workspace/transschema" \
  --bind "/scratch/general/vast/u1592362:/scratch/general/vast/u1592362" \
  --pwd /workspace/transschema/AgentFlow \
  "${IMAGE}" \
  "${PYTHON_IN_CONTAINER}" train/train_datamorpheragent.py --skip_dep_check "$@"

