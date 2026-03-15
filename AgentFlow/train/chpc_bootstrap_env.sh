#!/usr/bin/env bash
# Build or update a lightweight scratch Python runtime on top of the base SIF.
# This is for fast-changing Python deps that should not trigger a full image rebuild.

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

RUNTIME_VENV="${AGENTFLOW_RUNTIME_VENV:-/scratch/general/vast/u1592362/AgentFlow_runtime_venv_current}"
RUNTIME_ENV_ROOT="${AGENTFLOW_RUNTIME_ENV_ROOT:-/scratch/general/vast/u1592362/AgentFlow_runtime_envs}"
RUNTIME_REQUIREMENTS="/workspace/transschema/AgentFlow/train/chpc_runtime_requirements.txt"
GPU_RUNTIME_REQUIREMENTS="${AGENTFLOW_GPU_RUNTIME_REQUIREMENTS:-/workspace/transschema/AgentFlow/train/chpc_gpu_runtime_requirements.txt}"
ENABLE_GPU_OVERLAY="${AGENTFLOW_ENABLE_GPU_OVERLAY:-0}"
INSTALL_FLASH_ATTN_UTILS="${AGENTFLOW_INSTALL_FLASH_ATTN_UTILS:-1}"
PIP_CACHE_DIR="${AGENTFLOW_PIP_CACHE_DIR:-/scratch/general/vast/u1592362/pip_cache}"
FREEZE_FILE="${AGENTFLOW_RUNTIME_FREEZE:-${RUNTIME_VENV}.freeze.txt}"

mkdir -p "$(dirname "${RUNTIME_VENV}")"
mkdir -p "${RUNTIME_ENV_ROOT}"
mkdir -p "${PIP_CACHE_DIR}"

echo "Bootstrapping scratch runtime env:"
echo "  image=${IMAGE}"
echo "  venv=${RUNTIME_VENV}"
echo "  env_root=${RUNTIME_ENV_ROOT}"
echo "  requirements=${RUNTIME_REQUIREMENTS}"
echo "  gpu_requirements=${GPU_RUNTIME_REQUIREMENTS}"
echo "  enable_gpu_overlay=${ENABLE_GPU_OVERLAY}"
echo "  install_flash_attn_utils=${INSTALL_FLASH_ATTN_UTILS}"

export PIP_CACHE_DIR

exec apptainer exec \
  --bind "${REPO_ROOT}:/workspace/transschema" \
  --bind "/scratch/general/vast/u1592362:/scratch/general/vast/u1592362" \
  --pwd /workspace/transschema/AgentFlow \
  "${IMAGE}" \
  /bin/bash -lc "
set -euo pipefail

build_id=\$(date +%Y%m%d-%H%M%S)
new_venv=\"${RUNTIME_ENV_ROOT}/venv-\${build_id}\"
previous_target=\$(readlink \"${RUNTIME_VENV}\" 2>/dev/null || true)

python3.11 -m venv --system-site-packages \"\${new_venv}\"

\"\${new_venv}/bin/python\" -m pip install --upgrade \
  pip==24.3.1 \
  setuptools==75.8.0 \
  wheel==0.45.1

\"\${new_venv}/bin/python\" -m pip install \
  --requirement \"${RUNTIME_REQUIREMENTS}\"

if [[ \"${ENABLE_GPU_OVERLAY}\" == \"1\" && -f \"${GPU_RUNTIME_REQUIREMENTS}\" ]]; then
  \"\${new_venv}/bin/python\" -m pip install \
    --upgrade \
    --upgrade-strategy eager \
    --requirement \"${GPU_RUNTIME_REQUIREMENTS}\"
fi

if [[ \"${INSTALL_FLASH_ATTN_UTILS}\" == \"1\" ]]; then
  FLASH_ATTENTION_SKIP_CUDA_BUILD=TRUE \
  FLASH_ATTENTION_FORCE_BUILD=FALSE \
    \"\${new_venv}/bin/python\" -m pip install \
      --no-build-isolation \
      --no-cache-dir \
      --no-deps \
      --upgrade \
      flash-attn==2.7.4.post1
fi

INSTALL_FLASH_ATTN_UTILS=\"${INSTALL_FLASH_ATTN_UTILS}\" \
  \"\${new_venv}/bin/python\" - <<'PY'
import importlib
import os
import sys

torch = importlib.import_module('torch')
print(f'Resolved torch runtime: {torch.__version__}  cuda={torch.version.cuda}')

require_flash = os.environ.get('INSTALL_FLASH_ATTN_UTILS', '1') == '1'
if require_flash:
    try:
        importlib.import_module('flash_attn.bert_padding')
        print('flash_attn import check: OK')
    except Exception as exc:
        print(f'flash_attn import check failed: {exc}')
        sys.exit(1)
PY

\"\${new_venv}/bin/python\" -m pip freeze | sort > \"${FREEZE_FILE}\"

ln -sfn \"\${new_venv}\" \"${RUNTIME_VENV}\"

# Best-effort cleanup of older runtime envs. Busy NFS-backed envs may be left behind.
if compgen -G \"${RUNTIME_ENV_ROOT}/venv-*\" > /dev/null; then
  mapfile -t old_envs < <(ls -dt \"${RUNTIME_ENV_ROOT}\"/venv-* 2>/dev/null | tail -n +4)
  for old_env in \"\${old_envs[@]}\"; do
    rm -rf \"\${old_env}\" 2>/dev/null || true
  done
fi

echo
echo \"Scratch runtime ready.\"
echo \"  python=${RUNTIME_VENV}/bin/python\"
echo \"  freeze=${FREEZE_FILE}\"
if [[ -n \"\${previous_target}\" && \"\${previous_target}\" != \"\${new_venv}\" ]]; then
  echo \"  previous=\${previous_target}\"
fi
"
