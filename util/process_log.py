import os
import csv
import pandas as pd
import re

def read(filename):
    with open(filename) as f:
       return(f.read())
    
with open('output.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['name', 'len_id', 'max_len_id', 'target_id', 'max_target_id', 'target_per', 'is_perc', 'hint_source', 'anon_flag', 'target_length', 'source_length', 'join_flag', 'aggregate_flag', 'fd_flag', 'join_hints_truncate', 'aggregate_hints_truncate', 'critique_setting', 'critique_type', 'token_limit', 'model', 'log_dir', 'experiment_name', 'no_of_runs', 'hints_v3_truncates', 'intermediate_materialization', 'few_shot', 'combine_ask_and_configure', 'no_thinking', 'majority_voting'])

path = "/Users/jiazou/Downloads/thing/logs-auto-suggest-llm-21-04"
contents = os.listdir(path)
for content in contents:
    path_cont = f"/Users/jiazou/Downloads/thing/logs-auto-suggest-llm-21-04/{content}"
    if os.path.isdir(path_cont):
        contents2 = os.listdir(path_cont)
        for content2 in contents2:
            if content2 == 'args.log':
                rf = read(f"/Users/jiazou/Downloads/thing/logs-auto-suggest-llm-21-04/{content}/args.log") 
                rf = rf.strip()
                dict_match = re.search(r"\{.*?\}", rf)
                if dict_match:
                    dict_str = dict_match.group()
                    rf_temp = rf.replace(dict_str, "DICT_PLACEHOLDER")
                cont_split = re.split(r'[\n:]', rf_temp)
                cont_split = [s.replace("DICT_PLACEHOLDER", dict_str) for s in cont_split]
                cont_split.insert(0, content)
                vals = []
                for rwn, rw in enumerate(cont_split):
                    if rwn % 2 == 0:
                        vals.append(rw.strip())
                with open('output.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(vals)


