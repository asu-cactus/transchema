#!/usr/bin/env bash
# Run from AgentFlow/ on the CHPC compute node.
# Usage: bash train/chpc_oneclick_debug.sh

set -euo pipefail

# Load CUDA 12.8 — required for torch 2.7.0+cu128 on Blackwell (sm_120)
module purge
module load cuda/12.8
export CUDA_HOME=$(dirname $(dirname $(which nvcc)))
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

unset ROCR_VISIBLE_DEVICES
export CUDA_VISIBLE_DEVICES=0
export HF_HOME=/scratch/general/vast/u1592362/hf_cache

URL_FILE="${AGENTFLOW_VLLM_URL_FILE:-/tmp/agentflow_vllm_url.txt}"
LOG="/tmp/dm_smoke_$(date +%H%M%S).log"

echo "--- Step 1: clean up"
rm -f "${URL_FILE}" || true
ray stop --force >/dev/null 2>&1 || true

echo "--- Step 2: start smoke run (log: ${LOG})"
nohup python train/train_datamorpheragent.py --smoke_test >"${LOG}" 2>&1 &
PID=$!
echo "PID ${PID} — follow logs with:  tail -f ${LOG}"

echo "--- Step 3: waiting for vLLM to come up (model load takes 5-15 min)..."
for ((i=1; i<=900; i++)); do
  [[ -s "${URL_FILE}" ]] && break
  kill -0 "${PID}" 2>/dev/null || { echo "FAIL: process died — tail -n 40 ${LOG}"; tail -n 40 "${LOG}"; exit 1; }
  (( i % 30 == 0 )) && printf "  %ds elapsed...\n" "${i}"
  sleep 1
done

URL="$(tr -d '\r\n' < "${URL_FILE}" 2>/dev/null || true)"
[[ -z "${URL}" ]] && { echo "FAIL: URL file never appeared — tail -n 40 ${LOG}"; tail -n 40 "${LOG}"; exit 1; }

echo "--- Step 4: probe endpoint"
python train/debug_agentflow_issues.py \
  --config train/datamorpherconfig.yaml \
  --base-url "${URL}" \
  --chat-test || true

echo
echo "Done. PID=${PID}  log=${LOG}"
