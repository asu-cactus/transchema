#!/usr/bin/env bash
set -euo pipefail

error=0
for i in 1 2 3 4 5 6 9; do
  for (( j=0; j<=99; j++ )); do
    n=$(grep -R -F "\"Target${i}_${j}\"" ./data | wc -l || true)
    if [[ $n -eq 0 ]]; then
      echo "\"Target${i}_${j}\""
      ((error++))
    fi
  done
done

echo "$error"
       
