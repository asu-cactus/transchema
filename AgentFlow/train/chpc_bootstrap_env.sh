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

RUNTIME_VENV="${AGENTFLOW_RUNTIME_VENV:-/scratch/general/vast/u1592362/AgentFlow_runtime_venv}"
RUNTIME_REQUIREMENTS="/workspace/transschema/AgentFlow/train/chpc_runtime_requirements.txt"
PIP_CACHE_DIR="${AGENTFLOW_PIP_CACHE_DIR:-/scratch/general/vast/u1592362/pip_cache}"
FREEZE_FILE="${AGENTFLOW_RUNTIME_FREEZE:-${RUNTIME_VENV}.freeze.txt}"

mkdir -p "$(dirname "${RUNTIME_VENV}")"
mkdir -p "${PIP_CACHE_DIR}"

echo "Bootstrapping scratch runtime env:"
echo "  image=${IMAGE}"
echo "  venv=${RUNTIME_VENV}"
echo "  requirements=${RUNTIME_REQUIREMENTS}"

export PIP_CACHE_DIR

exec apptainer exec \
  --bind "${REPO_ROOT}:/workspace/transschema" \
  --bind "/scratch/general/vast/u1592362:/scratch/general/vast/u1592362" \
  --pwd /workspace/transschema/AgentFlow \
  "${IMAGE}" \
  /bin/bash -lc "
set -euo pipefail

recreate_venv=0
if [[ ! -x \"${RUNTIME_VENV}/bin/python\" ]]; then
  recreate_venv=1
elif [[ -f \"${RUNTIME_VENV}/pyvenv.cfg\" ]] && ! grep -q '^include-system-site-packages = true$' \"${RUNTIME_VENV}/pyvenv.cfg\"; then
  echo \"Existing venv is isolated; recreating as a layered venv with system site-packages.\"
  recreate_venv=1
fi

if [[ \"\${recreate_venv}\" == \"1\" ]]; then
  rm -rf \"${RUNTIME_VENV}\"
  python3.11 -m venv --system-site-packages \"${RUNTIME_VENV}\"
fi

\"${RUNTIME_VENV}/bin/python\" -m pip install --upgrade \
  pip==24.3.1 \
  setuptools==75.8.0 \
  wheel==0.45.1

\"${RUNTIME_VENV}/bin/python\" -m pip install \
  --requirement \"${RUNTIME_REQUIREMENTS}\"

\"${RUNTIME_VENV}/bin/python\" -m pip freeze | sort > \"${FREEZE_FILE}\"

echo
echo \"Scratch runtime ready.\"
echo \"  python=${RUNTIME_VENV}/bin/python\"
echo \"  freeze=${FREEZE_FILE}\"
"
