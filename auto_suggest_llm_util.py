import ast
import glob
import os
import time
import re

from sklearn.preprocessing import LabelEncoder

from agent import Agent
import csv
import pandas as pd
import logging
from datetime import datetime
from itertools import combinations
from llm.llm_models import TokenUsageTracker
from model.aggregation.pwr import predict_columns
from model.join.pwr import load_trained_model, predict_join_columns
from quality.quality import get_df, data_summary, data_profiling, schema_quality, fd_quality, data_quality, \
    data_morpher, schema_matching
from summary import load_tables, generate_transformation_hints
from util.utils import (create_connection, execute_sql,  execute_python,log_experiment_settings,
                        log_experiment_success, log_experiment_failed,
                        compare_lists_matching, get_test_info, log_experiment, calculate_cost_difference
                        #,preprocess_sql_script
                        )
from test_scope import get_test_cases_ids

from model.join.data import generate_features,is_single_column
from model.aggregation.data import generate_features_for_column


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

    return hints

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

    return hints
    
    
    
