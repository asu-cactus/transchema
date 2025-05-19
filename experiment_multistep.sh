export PYTHONPATH=$(pwd)

python3 critique_data.py \
  --len-id 6 \
  --max-len-id 6 \
  --target-id 0 \
  --max-target-id 0 \
  --target-per 25 \
  --no-perc \
  --hint-source v3 \
  --no-anon \
  --target-length 3 \
  --source-length 9 \
  --join-flag 0 \
  --aggregate-flag 0 \
  --fd-flag 0 \
  --join-hints-truncate 0.027387593197926163 0.8763891522960383 0.6923226156693141 0.8946066635038473 0.14038693859523377 0.8007445686755367 \
  --aggregate-hints-truncate 0.9 0.1 0.9 0.1 0.9 0.1 0.9 0.1 0.9 0.1 \
  --critique_setting fd metadata \
  --token-limit 120000 \
  --model gpt-4.1-mini \
  --log-dir logs \
  --experiment-name feature_v3_2 \
  --no-of-runs 1 \
  --hints-v3-truncates '{"t1":0.7,"t2":0.7,"t3":0.7,"t4":10,"t5":0.1,"t6":0.8,"t7":0.4,"t8":0.3,"t9":0.2,"t10":0.3,"t11":0.5,"t12":0.7,"t13":0.2}' \
  --intermediate-materialization-flag 1 \
  --use-old-prompt 0 \
  --combine-ask-and-configure 0 \
  --no-thinking 0 \
