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

unset ROCR_VISIBLE_DEVICES
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export HF_HOME="${HF_HOME:-/scratch/general/vast/u1592362/hf_cache}"
export PYTHONPATH="${REPO_ROOT}:${AGENTFLOW_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
RUNTIME_VENV="${AGENTFLOW_RUNTIME_VENV:-/scratch/general/vast/u1592362/AgentFlow_runtime_venv_current}"
LEGACY_RUNTIME_VENV="/scratch/general/vast/u1592362/AgentFlow_runtime_venv"
PYTHON_IN_CONTAINER="python3.11"

if [[ -x "${RUNTIME_VENV}/bin/python" ]]; then
  PYTHON_IN_CONTAINER="${RUNTIME_VENV}/bin/python"
  echo "Using scratch runtime env: ${RUNTIME_VENV}"
elif [[ -x "${LEGACY_RUNTIME_VENV}/bin/python" ]]; then
  PYTHON_IN_CONTAINER="${LEGACY_RUNTIME_VENV}/bin/python"
  echo "Using legacy scratch runtime env: ${LEGACY_RUNTIME_VENV}"
else
  echo "No scratch runtime env found at ${RUNTIME_VENV}."
  echo "For lightweight Python dependency updates without rebuilding the SIF, run:"
  echo "  APPTAINER_IMAGE=${IMAGE} bash AgentFlow/train/chpc_bootstrap_env.sh"
fi

# Avoid wandb login failures on batch/cluster runs unless the user explicitly configured it.
if [[ -z "${WANDB_API_KEY:-}" && -z "${WANDB_MODE:-}" ]]; then
  export WANDB_MODE=offline
fi

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

