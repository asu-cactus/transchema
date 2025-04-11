# decided through parameters
len_id = 1
max_len_id = 1
target_id = 12 #[11,18,22,25,62,10,16,31,38,5] # [18,2,32,33,96,16,27,78,91,18]
max_target_id = 13
target_per = 25
is_perc = False
hint_source = "v2" # v1_kv, v1_text or v2(Xuanmao's hints)
anon_flag = False

target_length = int(max(3,10*0.31342417815924284))
source_length = int(max(3,10*0.9682615757193975))

join_flag = 1
aggregate_flag = 1

join_hints_truncate = [0.027387593197926163,0.8763891522960383,0.6923226156693141,0.8946066635038473,0.14038693859523377,0.8007445686755367]
aggregate_hints_truncate = [0.9,0.1,0.9,0.1,0.9,0.1,0.9,0.1,0.9,0.1]

fd_flag = 0
token_limit = 120000
model = 'gpt-4-turbo'

log_dir = "logs-auto-suggest-llm-18-03"

experiment_name = "text_features"

no_of_runs = 3
majority_voting = no_of_runs // 2 + 1