import ast
import glob
import os
import time
import re

from sklearn.preprocessing import LabelEncoder

# from agent import Agent
import csv
import pandas as pd
import logging
from datetime import datetime
from itertools import combinations
from llm.llm_models import TokenUsageTracker
# from model.aggregation.pwr import predict_columns
# from model.join.pwr import load_trained_model, predict_join_columns
# from quality.quality import get_df, data_summary, data_profiling, schema_quality, fd_quality, data_quality, \
    # data_morpher, schema_matching
# from summary import load_tables, generate_transformation_hints
from util.utils import (create_connection, execute_sql,  execute_python,log_experiment_settings,
                        log_experiment_success, log_experiment_failed,
                        compare_lists_matching, get_test_info, log_experiment
                        #,preprocess_sql_script
                        )
from test_scope import get_test_cases_ids

from model.join.data import generate_features,is_single_column
from model.aggregation.data import generate_features_for_column
import auto_suggest_llm_prompts as prt
import tiktoken
from quality.quality import analyze_functional_dependencies,data_profiling,data_summary
from valentine import valentine_match
import valentine.algorithms as algorithms

# prt.get_prompt("join",                allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information,hints)
# prt.get_prompt("group_by_aggregate",  allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information,hints)
# prt.get_prompt("union",               allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information,hints="")
# prt.get_python_script("python_script",allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,ss,target_file_location)
def get_prompt(prompt_type, allowed_operation_list,
                operation_history,target_data_name,target_data_schema,
                target_samples,file_count,source_data_name_list,source_data_schema_list, directory,len_idx_target_idx,
                source_samples_list,model, error_string = "",max_tokens = False, target_perc = 10, is_perc = True, target_length = 3,target_file_location = "") : 
    
    # we can generate hints here itself
    # we need these information
    # file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx

    # 2 types of tokens 
    # static : content in the prompt without target examples
    # dynamic : target_examples
    max_tokens = 128000 # for gpt4turbo 
    source_information = get_source(file_count, source_data_name_list,
                source_data_schema_list, source_samples_list)
    encoding = tiktoken.encoding_for_model("gpt-4-turbo")

    if prompt_type == 'get_next_operator' :
        
        static_prompt = prt.get_next_operator_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,"",file_count, source_information)[0]
        static_prompt_length = len(encoding.encode(static_prompt))
        target_samples = get_target_samples(directory,len_idx_target_idx,target_perc, is_perc, target_length, max_tokens, static_prompt_length,encoding)[0]
        prompt = prt.get_next_operator_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information)[0]
        # print(static_prompt_length)
        # print(str(len(encoding.encode(str(target_samples)))))
        # print(str(len(encoding.encode(prompt))))

    if prompt_type == 'join' :
        hints = get_join_hints(file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx)[0]
        static_prompt = prt.get_join_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,"",file_count, source_information,hints)[0]
        static_prompt_length = len(encoding.encode(static_prompt))
        target_samples = get_target_samples(directory,len_idx_target_idx,target_perc, is_perc, target_length, max_tokens, static_prompt_length, encoding)[0]
        prompt = prt.get_join_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information,hints)[0]

    if prompt_type == 'group_by_aggregate' :
        hints = get_groupby_aggregate_hints(file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx)[0]
        static_prompt = prt.get_group_by_aggregate_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,"",file_count, source_information, hints)[0]
        static_prompt_length = len(encoding.encode(static_prompt))
        target_samples = get_target_samples(directory,len_idx_target_idx,target_perc, is_perc, target_length, max_tokens, static_prompt_length, encoding)[0]
        prompt = prt.get_group_by_aggregate_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information,hints)[0]

    if prompt_type == 'union' :
        static_prompt = prt.get_union_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,"",file_count, source_information)[0]
        static_prompt_length = len(encoding.encode(static_prompt))
        target_samples = get_target_samples(directory,len_idx_target_idx,target_perc, is_perc, target_length, max_tokens, static_prompt_length, encoding)[0]
        prompt = prt.get_union_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information)[0]
        
    if prompt_type == 'python_script' :
        source_information_with_location = get_source_with_location(file_count, source_data_name_list,source_data_schema_list, source_samples_list, directory, len_idx_target_idx) 
        # target_file_location = directory + '/length' + len_idx_target_idx + '/target_multisource.csv'
        print(error_string)
        static_prompt = prt.get_python_script(allowed_operation_list,operation_history,target_data_name,target_data_schema,"",file_count, source_information_with_location, target_file_location, error_string)[0]
        static_prompt_length = len(encoding.encode(static_prompt))
        target_samples = get_target_samples(directory,len_idx_target_idx,target_perc, is_perc, target_length, max_tokens, static_prompt_length, encoding)[0]
        prompt = prt.get_python_script(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information_with_location, target_file_location, error_string)[0]

    # print(prompt)

    if(len(encoding.encode(prompt)) > max_tokens) :
        return ['-1']  
    
    return [prompt]
        # Static Dynamic tokens
        # Dynamic tokens 

def get_target_string(df, rem_tokens, encoding) :

    # string should be target rows in list
    examples_l = df.values.tolist()
    examples = str(examples_l)
    
    # if all passes do not check further 
    if(len(encoding.encode(examples)) < rem_tokens) :
        return examples    

    # if not then do binary search on exact number of examples that can be in there 
    l = 0
    r = len(examples_l)-1
    ans = 0
    while(l < r) :

        mid = (l+r)//2

        # print(l,mid,r)
        
        #examples upto mid 
        temp_l = examples_l[:mid+1]
        #how much string is being used 
        temp = str(temp_l)
        encode_len = len(encoding.encode(temp))

        # print(rem_tokens, encode_len)

        if(encode_len <= rem_tokens) :
            ans = mid
            l = mid + 1
        elif(encode_len > rem_tokens) :
            r = mid - 1
        
    # print('ans :', ans)
    temp_l = examples_l[:ans]
    # print(len(encoding.encode(str(temp_l))))
    return [str(temp_l)]





def get_target_samples(directory,len_idx_target_idx,target_perc, is_perc, target_length, max_tokens, static_prompt_length, encoding) :
    # print(directory,len_idx_target_idx, target_perc,is_perc, target_length, max_tokens, static_prompt_length)
    target_csv_path = directory + '/length' + len_idx_target_idx + '/target.csv'
    target_df = pd.read_csv(target_csv_path, low_memory=False)

    # sampling 
    if(is_perc) : 
        target_df_sampled = target_df.sample(frac = target_perc/100, replace = False)
    else : 
        target_df_sampled = target_df.sample(n = target_length, replace = False)
    # print(static_prompt_length)
    target_samples_string = get_target_string(target_df_sampled, max_tokens - static_prompt_length - 2000 - 4096,encoding) #-1000 buffer for good measures

    return [target_samples_string]


    


def get_source(file_count, source_data_name_list,
             source_data_schema_list, source_samples_list) :
    ss = ""
    for i in range(file_count) :
        ss+= '\tSource {i}:\n'.format(i = i)
        ss+= '\tSource {i} Name: {source_data_name_list}\n'.format(i = i, source_data_name_list = source_data_name_list[i])
        ss+= '\tSource {i} Schema: {source_data_schema_list}\n'.format(i = i,source_data_schema_list = source_data_schema_list[i])
        ss+= '\tSource {i} Examples: {source_samples_list}\n'.format(i = i,source_samples_list = source_samples_list[i])
    return ss

def get_source_with_location(file_count, source_data_name_list,
             source_data_schema_list, source_samples_list, main_directory, len_idx_target_idx) :
    ss = ""
    for i in range(file_count) :
        ss+= '\tSource {i}:\n'.format(i = i)
        ss+= '\tSource {i} Name: {source_data_name_list}\n'.format(i = i, source_data_name_list = source_data_name_list[i])
        ss+= '\tSource {i} Schema: {source_data_schema_list}\n'.format(i = i,source_data_schema_list = source_data_schema_list[i])
        ss+= '\tSource {i} Examples: {source_samples_list}\n'.format(i = i,source_samples_list = source_samples_list[i])
        ss+= '\tSource {i} File Location: {main_directory}/length{len_idx_target_idx}/test_{i}.csv\n'.format(i = i, main_directory = main_directory, len_idx_target_idx = len_idx_target_idx)
    return ss     

def create_logger(log_dir, pipeline_len_start_idx,target_start_idx,max_target_idx):
        # Get current system time
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create the log file name with the current time
        log_file = f"all_similarity_scores_auto_suggest_llm_len{pipeline_len_start_idx}_target{target_start_idx}_source{max_target_idx}_{current_time}.log"

        # Check if the log directory exists, create it if it does not
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Setup logging
        logging.basicConfig(filename=os.path.join(log_dir, log_file), level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s', filemode='a+')
        return logging.getLogger()

def get_operation(s) :
    match = re.search(r'\$(.*?)\$', s)
    if match:
        extracted_word = match.group(1)
        return extracted_word
    else:
        extracted_word = "No match found"

def get_columns(s) :
    matches = re.findall(r'\$(.*?)\$', s)
    return matches

def get_columns_join(s) :
    result = re.search(r'\$(.*?)\$', s)
    if result:
        extracted_content = result.group(1)
        return extracted_content

    return "No match found"

def get_columns_aggr(s) :
    elements = s.strip('[]').split(',')

# Remove the quotes and dollar signs from each element
    elements = [element.strip(' ') for element in elements]

    elements = [element.strip('"') for element in elements]

    elements = [element.strip('$') for element in elements]

    res = [elements[:-2],elements[-2],elements[-1]]

    return res


def load_tables(directory,source_data_name_list,len_idx_target_idx):
    tables = {}
    for i in range(len(source_data_name_list)) : 
        tables[source_data_name_list[i]] = pd.read_csv(os.path.join(directory ,'length' + len_idx_target_idx + '/test_' + str(i) + '.csv'))
        tables[source_data_name_list[i]] = tables[source_data_name_list[i]].drop(tables[source_data_name_list[i]].columns[0], axis=1)
    return tables

def get_join_hints(file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx) :
    hints = ""
    features = []
    tables = load_tables(directory,source_data_name_list,len_idx_target_idx)
    # print(tables)

    for table_name1, table_name2 in combinations(tables.keys(), 2):
        table1 = tables[table_name1]
        table2 = tables[table_name2]
        columns1 = table1.columns
        columns2 = table2.columns
        total_columns1 = len(columns1)
        total_columns2 = len(columns2)

        for col1 in columns1 :
            for col2 in columns2 :
                if(table1[col1].dtype == table2[col2].dtype) :
                    hint = ' - '
                    pos1 = columns1.get_loc(col1)
                    pos2 = columns2.get_loc(col2)
                    feature = generate_features(table1[col1], table2[col2], table1, table2, pos1, pos2, total_columns1, total_columns2, is_single_column([(col1, col2)]))
                    hint+=table_name1+'.'+col1+'<->'+table_name2+'.'+col2+' : '
                    hint+='''(distinct_value_ratio of {t1}.{c1} : {f[0]}, distinct_value_ratio of {t2}.{c2} : {f[1]}),value-overlap: (Jaccard Similarity : {f[2]}, Jaccard containment : {f[3]}),value-range-overlap: {f[4]},leftness of {t1}.{c1} : {f[6]},leftness of {t2}.{c2} : {f[7]},sortedness of {t1}.{c1} : {f[8]},sortedness of {t2}.{c2} : {f[9]},ratio of row-count : {f[10]})\n'''.format(c1=col1,c2=col2,t1=table_name1,t2=table_name2,f=feature)
                    hints += hint

    return [hints]

def get_groupby_aggregate_hints(file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx) :
    hints = ""
    features = []
    tables = load_tables(directory,source_data_name_list,len_idx_target_idx)

    for table_name, table in tables.items():
        columns = table.columns
        total_columns = len(columns)

        for pos, col_name in enumerate(columns):
            try : 
                hint = '- '
                col = table[col_name]
                # Generate features
                feature = generate_features_for_column(col, col_name, pos, total_columns)
                hint += table_name+'.'+col_name+ ' : '
                hint += '''(Distinct value count : {f[0]}, Distinct Value Ratio : {f[1]}, Column Data Type : {f[2]}, Leftness : {f[3]}, Emptiness : {f[4]}, Value_Range : {f[5]}, ratio of distinct value count to range : {f[6]}, Peak Frequency : {f[7]})\n'''.format(f = feature)
                hints += hint
            except :
                pass

    return [hints]

def cost_compare(cost1, cost2, model) :
    cost = dict()
    cost["total_cost"] = cost2["total_cost"] - cost1["total_cost"]
    cost["detailed_cost"] = dict()
    if(model in cost1["detailed_cost"].keys()) : 
        cost["detailed_cost"][model] = {'completion_tokens' : cost2["detailed_cost"][model]['completion_tokens'] - cost1["detailed_cost"][model]['completion_tokens'], 'prompt_tokens' : cost2["detailed_cost"][model]["prompt_tokens"] - cost1["detailed_cost"][model]['prompt_tokens'], 'cost' : cost2["detailed_cost"][model]["cost"] - cost1["detailed_cost"][model]["cost"]}
    else : 
        cost["detailed_cost"][model] = cost2["detailed_cost"][model]

    # print('calculated Cost : ', cost)

    return cost

def increment_count(q) :
    q['total'] += 1
    q['in_task'] += 1
    return 

#llm_client,model,prompt, q_count, cost_summary, token_tracker, type = "Ask For Operator"
def query_gpt(llm_model,model, prompt, q_count, logger, cost_summary, token_tracker,type) :
    start_time = time.time()
    logger.info("Query of Type : {type_}".format(type_ = type))
    #run the prompt and get the result 
    res = llm_model.gpt(prompt[0])
    #log the prompt 
    logger.info('Prompt to ask for operator : {prompt}'.format(prompt = prompt[0]))
    # log the result 
    logger.info('Result Recieved :  {res}'.format(res = res[0]))
    end_time = time.time()
    #calculate append incremental cost in cost_summary, the last one will be the total task cost 
    cost_summary.append(token_tracker.cost_summary())

    #calculate cost associated with this task
    cost = cost_compare(cost_summary[-2],cost_summary[-1],model) 
    # print('Cost : ', cost)
    
    #log that cost
    logger.info('Cost of the query : {cost}'.format(cost = cost))
    logger.info('Time taken for this prompt : {time_elapsed}'.format(time_elapsed = end_time - start_time))
    
    #increment task counts
    increment_count(q_count)
    
    return res
    

def calculate_score(gt_df, tgt_df) :
    # Match Functional Dependencies 
    fd_gt, key_gt = analyze_functional_dependencies(gt_df)
    fd_tgt, key_tgt = analyze_functional_dependencies(tgt_df)

    print(fd_gt)
    print(key_gt)

    total_fds = len(fd_gt)
    total_keys = len(key_gt)
    
    discovered_fd = 0
    for fd in fd_gt : 
        if(fd in fd_tgt) : 
            print(fd)
            discovered_fd += 1

    fd_score = discovered_fd/total_fds

    discovered_keys = 0
    for key in key_gt : 
        if key in key_tgt : 
            print(key)
            discovered_keys += 1

    key_score = discovered_keys / total_keys
    
    # df_gt_schema = {col: gt_df[col].dtype for col in gt_df.columns}
    # df_tgt_schema = {col: tgt_df[col].dtype for col in tgt_df.columns}

    matcher = algorithms.Cupid()

    # Match schemas
    matches = valentine_match(gt_df, tgt_df,matcher)
    gt_df_columns = gt_df.columns

    gt_df_columns = set(gt_df.columns)
    matched_columns = set(match[0] for match in matches)
    
    column_mapping_score = len(matched_columns) / len(gt_df_columns)
    

    return [fd_score, key_score, column_mapping_score]
    
    
