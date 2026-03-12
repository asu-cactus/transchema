#!/usr/bin/env bash
set -euo pipefail

# One-command CHPC debug helper for DataMorpher AgentFlow.
# Run from AgentFlow/ directory:
#   bash train/chpc_oneclick_debug.sh

URL_FILE="${AGENTFLOW_VLLM_URL_FILE:-/tmp/agentflow_vllm_url.txt}"
CONFIG_PATH="${CONFIG_PATH:-train/datamorpherconfig.yaml}"
TRAIN_CMD="${TRAIN_CMD:-python train/train_datamorpheragent.py --smoke_test}"
WAIT_SECONDS="${WAIT_SECONDS:-120}"
LOG_FILE="${LOG_FILE:-/tmp/datamorpher_smoke_$(date +%Y%m%d_%H%M%S).log}"

echo "== DataMorpher one-click debug =="
echo "URL file   : ${URL_FILE}"
echo "Config     : ${CONFIG_PATH}"
echo "Train cmd  : ${TRAIN_CMD}"
echo "Wait (sec) : ${WAIT_SECONDS}"
echo "Log file   : ${LOG_FILE}"
echo

echo "[1/5] Cleaning stale state..."
rm -f "${URL_FILE}" || true
ray stop --force >/dev/null 2>&1 || true

echo "[2/5] Starting smoke run in background..."
nohup bash -lc "${TRAIN_CMD}" >"${LOG_FILE}" 2>&1 &
TRAIN_PID=$!
echo "Started PID: ${TRAIN_PID}"

echo "[3/5] Waiting for URL file..."
URL=""
for ((i=1; i<=WAIT_SECONDS; i++)); do
  if [[ -s "${URL_FILE}" ]]; then
    URL="$(tr -d '\r\n' < "${URL_FILE}")"
    break
  fi

  if ! kill -0 "${TRAIN_PID}" 2>/dev/null; then
    echo
    echo "[FAIL] Training process exited before URL file appeared."
    echo "Check log: ${LOG_FILE}"
    echo "Quick view: sed -n '1,200p' ${LOG_FILE}"
    exit 1
  fi

  sleep 1
done

if [[ -z "${URL}" ]]; then
  echo
  echo "[FAIL] URL file did not appear within ${WAIT_SECONDS}s."
  echo "Check log: ${LOG_FILE}"
  echo "Quick view: sed -n '1,200p' ${LOG_FILE}"
  exit 1
fi

echo "[OK] URL found: ${URL}"

echo "[4/5] Checking listener..."
PORT="$(echo "${URL}" | sed -E 's#.*:([0-9]+)/v1#\1#')"
if [[ "${PORT}" =~ ^[0-9]+$ ]]; then
  if ss -ltnp 2>/dev/null | grep -q ":${PORT} "; then
    echo "[OK] Port ${PORT} is listening."
  else
    echo "[WARN] No listener seen on port ${PORT} yet."
  fi
else
  echo "[WARN] Could not parse port from URL: ${URL}"
fi

echo "[5/5] Running endpoint/tool debugger..."
python train/debug_agentflow_issues.py \
  --config "${CONFIG_PATH}" \
  --base-url "${URL}" \
  --chat-test || true

echo
echo "== Done =="
echo "Background training PID: ${TRAIN_PID}"
echo "Log file: ${LOG_FILE}"
echo
echo "Useful commands:"
echo "  Follow logs:   sed -n '1,220p' ${LOG_FILE}"
echo "  Check process: ps -p ${TRAIN_PID} -f"
echo "  Stop process:  kill ${TRAIN_PID}"
