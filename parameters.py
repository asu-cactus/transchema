# decided through parameters
len_id = 5
max_len_id = 5
target_id = 12 #[11,18,22,25,62,10,16,31,38,5] # [18,2,32,33,96,16,27,78,91,18]
max_target_id = 40
target_per = 25
is_perc = False
hint_source = "v2" # v1_kv, v1_text or v2(Xuanmao's hints)
anon_flag = False

target_length = int(max(3,10*0.31342417815924284))
source_length = int(max(3,10*0.9682615757193975))

join_flag = 0
aggregate_flag = 0

join_hints_truncate = [0.027387593197926163,0.8763891522960383,0.6923226156693141,0.8946066635038473,0.14038693859523377,0.8007445686755367]
aggregate_hints_truncate = [0.9,0.1,0.9,0.1,0.9,0.1,0.9,0.1,0.9,0.1]


fd_flag = 0
token_limit = 60000
model = 'gpt-4o-mini'

log_dir = "logs-auto-suggest-llm-21-04"

experiment_name = "feature_v3_2"

no_of_runs = 1 
majority_voting = no_of_runs // 2 + 1

# BEGIN hints_v3_truncates
hints_v3_truncates = {
    # join conditions
    't1': 0.7, # [0.8,0.7,0.5,0.5] jaccard similarity > t1
    't2': 0.7, # [0.8,0.7,0.5,0.5] jaccard containment > t2
    't3': 0.7, # [0.8,0.7,0.5,0.5] value range overlap > t3
    't4': 10, # [10] number of rows in the source table > t4
    # join type conditions
    't5': 0.1, # [0.1,0.3,0.4,0.5] missing value ratio(target table) > t5
    't6': 0.8, # [0.8,0.4] jaccard containment > t6 
    't7': 0.4, # [0.4,0.8] jaccard containment < t7 
    # group by hints                 
    't8': 0.3, # [0.1,0.3,0.5,0.7] distinct value ratio < t8 
    't9': 0.2, # [0.1,0.2,0.3,0.5] emptiness < t9 
    't10': 0.3, # [0.5,0.3,0.1,0.05] peak_frequency > t10
    't11': 0.5, # [0.3,0.5,0.7,0.9] value_range < t11
    't12': 0.7, # [0.9,0.7,0.5,0.3] leftness > t12
    #union hints 
    't13': 0.2 # value range overlap < t13
    }
# END hints_v3_truncates

intermediate_materialization_flag = 0
use_old_prompt = 0
combine_ask_and_configure = 0
no_thinking = 0
