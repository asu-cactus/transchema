export PYTHONPATH=$(pwd)

python3 critique_data.py \
  --len_id 1 \
  --max_len_id 1 \
  --target_id 23 \
  --max_target_id 24 \
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
  --critique_setting metadata \
  --critique_type soft \
  --token-limit 120000 \
  --model gpt-4.1-mini \
  --log-dir logs \
  --experiment-name majority_voting_check \
  --no_of_runs 3 \
  --hints-v3-truncates '{"t1":0.3,"t2":0.3,"t3":0.3,"t4":10,"t5":0.1,"t6":0.4,"t7":0.8,"t8":0.7,"t9":0.3,"t10":0.5,"t11":0.3,"t12":0.3,"t13":0.2}' \
  --intermediate_materialization
  # #--use_old_prompt 
  # --combine_ask_and_configure \
  # --no_thinking \