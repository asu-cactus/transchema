from test_scope import get_test_cases_ids
from llm.llm_models import TokenUsageTracker, LLMClient
from util.utils import get_test_info, execute_python
from validation.hard_match import compare_lists_matching
from validation.soft_match import compare_lists_matching_soft
from padding_match import pad_comp
import time
import auto_suggest_llm_prompts as prt
from auto_suggest_llm_util import (
    get_source,
    get_operation,
    get_columns,
    get_source_with_location,
    cost_compare,
    query_gpt,
    get_columns_aggr,
    get_columns_join,
    get_prompt,
    get_filtered_functional_dependency,
    calculate_score
)
from log_util.log_util import create_logger
import parameters as p
import pandas as pd
import re
import sys
from pathlib import Path
import os
import traceback
import argparse
import json

from methods.multi_step import precursor
from methods.critique import critique

from auto.main import Autologtuple,sheet_dir,creds_path, sheets


def avg_tup(list_tup):
    avg_cost = 0
    avg_lat = 0
    for tup in list_tup:
        avg_cost += tup[3]
        avg_lat += tup[4]
    avg_cost = avg_cost/len(list_tup)
    avg_lat = avg_lat/len(list_tup)
    
    avg = (list_tup[0][0], avg_cost, avg_lat)
    return avg

def avg_tup_(list_tup):
    print("_________________________")
    print(f"averaging {list_tup}")
    avg_cost = 0
    avg_lat = 0
    avg_score = 0
    for tup in list_tup:
        avg_cost += tup[3]
        avg_lat += tup[4]
        avg_score += tup[2]
    avg_cost = avg_cost/len(list_tup)
    avg_lat = avg_lat/len(list_tup)
    avg_score = avg_score/len(list_tup)
    #here
    avg = (list_tup[0][1], avg_score,avg_cost, avg_lat)
    return avg

def ms(length, id, log_dir,experiment_name):
    results = [] 
    true_tup = []
    false_tup = []
    true_tup_ = []
    false_tup_ = []
    for i in range(0,p.no_of_runs):
        try:
            ms_info = precursor(length, id, log_dir,experiment_name,i)
        except Exception as e:
            print("".join(traceback.format_exc()))
            ms_info = ("precursor error " + str(e))
        #print(ms_info)
        results.append(ms_info)
    
    for tup in results:
        Autologtuple((f"{length}_{id}",) + tup,
                     sheet_dir["sheet_2"],
                     worksheet_name=sheets["sm"],
                     creds_file=creds_path
                    )
        if tup[1] == True:
            true_tup_.append(tup)
            #print(f"{tup} in true tup")
        else:
            #print(f"{tup} in false tup")
            false_tup_.append(tup)
            
        if tup[0] == True:
            true_tup.append(tup)
            #print(f"{tup} in true tup")
        else:
            #print(f"{tup} in false tup")
            false_tup.append(tup)
    
    
    if len(true_tup_) >= p.majority_voting:
        print(f"avging {true_tup_}")
        avged_tup_ = avg_tup_(true_tup_)
    else: 
        print(f"avging {false_tup_}")
        avged_tup_ = avg_tup_(false_tup_)
        
    if len(true_tup) >= p.majority_voting:
        avged_tup = avg_tup(true_tup)
    else:
        avged_tup = avg_tup(false_tup)     
    #
    return avged_tup + avged_tup_

def crit(length, id_, experiment_name):
    a_results = []
    ab_results = []
    abc_results = []
    
    #for strict match
    a_true = []
    a_false = []
    ab_true = []
    ab_false = []
    abc_true = []
    abc_false = []
    
    #for soft match
    a_true_ = []
    a_false_ = []
    ab_true_ = []
    ab_false_ = []
    abc_true_ = []
    abc_false_ = []
    
    for i in range(0,p.no_of_runs):
        # def critique(length, id_, nature, log_dir_, flags, is_def, i_, experiment_name):
        abl_a = critique(length, id_, "prompts/hard_critique.txt", f"crit_logs/{length}_{id_}/", [1,0,0],0,i, experiment_name)
        
        abl_ab = critique(length, id_, "prompts/soft_critique.txt", f"crit_logs/{length}_{id_}/", [1,1,0],1,i, experiment_name)
        
        abl_abc = critique(length, id_, "prompts/soft_critique.txt", f"crit_logs/{length}_{id_}/", [1,1,1],1,i, experiment_name)

        a_results.append(abl_a)
        ab_results.append(abl_ab)
        abc_results.append(abl_abc)
    
    for tup in a_results:
        Autologtuple((f"{length}_{id_}",) + tup,
                     sheet_dir["sheet_2"],
                     worksheet_name=sheets["sc"],
                     creds_file=creds_path
                    )
        if tup[1] == True:
            a_true_.append(tup)
        else:
            a_false_.append(tup)
        if tup[0] == True:
            a_true.append(tup)
        else:
            a_false.append(tup)
    for tup in ab_results:
        Autologtuple((f"{length}_{id_}",) + tup,
                     sheet_dir["sheet_2"],
                     worksheet_name=sheets["sc"],
                     creds_file=creds_path
                    )
        if tup[1] == True:
            ab_true_.append(tup)
        else:
            ab_false_.append(tup)
        if tup[0] == True:
            ab_true.append(tup)
        else:
            ab_false.append(tup)
    for tup in abc_results:
        Autologtuple((f"{length}_{id_}",) + tup,
                     sheet_dir["sheet_2"],
                     worksheet_name=sheets["sc"],
                     creds_file=creds_path
                    )
        if tup[1] == True:
            abc_true_.append(tup)
        else:
            abc_false_.append(tup)
        if tup[0] == True:
            abc_true.append(tup)
        else:
            abc_false.append(tup)
    
    if len(a_true) >= p.majority_voting:
        avg_a  = avg_tup(a_true)
    else:
        avg_a = avg_tup(a_false)
    if len(a_true_) >= p.majority_voting:
        avg_a_ = avg_tup_(a_true_)
    else:
        avg_a_ = avg_tup_(a_false_)
    
    if len(ab_true) >= p.majority_voting:
        avg_ab  = avg_tup(ab_true)
    else:
        avg_ab = avg_tup(ab_false)
    if len(ab_true_) >= p.majority_voting:
        avg_ab_ = avg_tup_(ab_true_)
    else:
        avg_ab_ = avg_tup_(ab_false_)
        
    if len(abc_true) >= p.majority_voting:
        avg_abc  = avg_tup(abc_true)
    else:
        avg_abc = avg_tup(abc_false)
    if len(abc_true_) >= p.majority_voting:
        avg_abc_ = avg_tup_(abc_true_)
    else:
        avg_abc_ = avg_tup_(abc_false_)
    
    
    avg_results = [avg_a + avg_a_, avg_ab + avg_ab_, avg_abc + avg_abc_]
    print("CRITIQUE FINAL RESULTS:")
    print(avg_results)
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    max_val = -1
    max_ind = 0
    i = 0
    
    for i, result in enumerate(avg_results):
        if result[4] > max_val:
            max_val = result[4]
            max_ind = i
            
    avg_results[max_ind] += ('MAX',)
    return avg_results

def get_parser():
    parser = argparse.ArgumentParser(description='Critique Data Script Parameterization')

    # Scalar integer parameters
    parser.add_argument('--len-id', type=int, default=5, help='Len ID')
    parser.add_argument('--max-len-id', type=int, default=5, help='Max Len ID')
    parser.add_argument('--target-id', type=int, default=12, help='Target ID')
    parser.add_argument('--max-target-id', type=int, default=40, help='Max Target ID')
    parser.add_argument('--target-per', type=int, default=25, help='Target Percentage')

    # Boolean flags
    parser.add_argument('--is-perc', action='store_true', help='Set is_perc to True')
    parser.add_argument('--no-perc', dest='is_perc', action='store_false', help='Set is_perc to False')
    parser.set_defaults(is_perc=False)

    parser.add_argument('--hint-source', type=str, default='v3',
                        choices=['v1_kv', 'v1_text', 'v2', 'v3'],
                        help='Hint source selection')
    parser.add_argument('--anon-flag', action='store_true', help='Set anon_flag to True')
    parser.add_argument('--no-anon', dest='anon_flag', action='store_false', help='Set anon_flag to False')
    parser.set_defaults(anon_flag=False)

    # Computed lengths (override if desired)
    parser.add_argument('--target-length', type=int,
                        default=int(max(3, 10 * 0.31342417815924284)),
                        help='Computed target length')
    parser.add_argument('--source-length', type=int,
                        default=int(max(3, 10 * 0.9682615757193975)),
                        help='Computed source length')

    # Flow control flags
    parser.add_argument('--join-flag', type=int, default=0, help='Join flag')
    parser.add_argument('--aggregate-flag', type=int, default=0, help='Aggregate flag')
    parser.add_argument('--fd-flag', type=int, default=0, help='Functional dependency flag')

    # Lists of floats
    parser.add_argument('--join-hints-truncate', type=float, nargs='+',
                        default=[0.027387593197926163, 0.8763891522960383, 0.6923226156693141,
                                 0.8946066635038473, 0.14038693859523377, 0.8007445686755367],
                        help='Join hints truncate thresholds')
    parser.add_argument('--aggregate-hints-truncate', type=float, nargs='+',
                        default=[0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1],
                        help='Aggregate hints truncate thresholds')

    # Other parameters
    parser.add_argument('--token-limit', type=int, default=120000, help='Token limit')
    parser.add_argument('--model', type=str, default='gpt-4-turbo', help='Model name')
    parser.add_argument('--log-dir', type=str, default='logs-auto-suggest-llm-21-04', help='Log directory')
    parser.add_argument('--experiment-name', type=str, default='feature_v3_2', help='Experiment name')
    parser.add_argument('--no-of-runs', type=int, default=1, help='Number of runs')

    # Complex dict via JSON
    default_hints = {
        't1': 0.7, 't2': 0.7, 't3': 0.7, 't4': 10,
        't5': 0.1, 't6': 0.8, 't7': 0.4,
        't8': 0.3, 't9': 0.2, 't10': 0.3, 't11': 0.5, 't12': 0.7, 't13': 0.2
    }
    parser.add_argument('--hints-v3-truncates', type=json.loads, default=default_hints,
                        help='JSON string for hints_v3_truncates dict')

    return parser

def main():

    args = get_parser().parse_args()

    # Unpack parameters
    p.len_id = args.len_id
    p.max_len_id = args.max_len_id
    p.target_id = args.target_id
    p.max_target_id = args.max_target_id
    p.target_per = args.target_per
    p.is_perc = args.is_perc
    p.hint_source = args.hint_source
    p.anon_flag = args.anon_flag
    p.target_length = args.target_length
    p.source_length = args.source_length
    p.join_flag = args.join_flag
    p.aggregate_flag = args.aggregate_flag
    p.fd_flag = args.fd_flag
    p.join_hints_truncate = args.join_hints_truncate
    p.aggregate_hints_truncate = args.aggregate_hints_truncate
    p.token_limit = args.token_limit
    p.model = args.model
    p.log_dir = args.log_dir
    p.experiment_name = args.experiment_name
    p.no_of_runs = args.no_of_runs
    p.majority_voting = p.no_of_runs // 2 + 1
    p.hints_v3_truncates = args.hints_v3_truncates

    length = p.len_id
    start = p.target_id
    end = p.max_target_id + 1
    Autologtuple(("Start", "Test:", f"{length}_{start}",f"{length}_{end}",),sheet_dir["sheet_1"],
                creds_file=creds_path )

    cases = list(range(start,end))

    experiment_name = p.experiment_name

    # lengths = [
    #   "Target3_11", 
    # ]



    # Get the path to credentials.json relative to the autologger package
    
    # for leng in lengths:
    #     length = int(leng[6])
    #     case = int(leng[8:])
    #     case_path = f"{length}_{case}"
    #     log_dir = f"crit_logs/{case_path}"

    for case in cases : 

        case_path = f"{length}_{case}"
        log_dir = f"crit_logs/{case_path}"
      
        try:
            #compute multisource
            ms_info = ms(length, case, log_dir, experiment_name)
            
            # Format as a single row with consistent columns
            #print(f"case_path: {case_path} + ms_info: {ms_info}")
            result = (case_path,) + ms_info 
            
            Autologtuple(
                result,
                sheet_dir["sheet_1"],
                worksheet_name=sheets["am"],
                creds_file=creds_path
            )
            
            # critique iff ms is wrong
            if not result[1]:
                crit_info = crit(length, case, experiment_name)

                for crit_ in crit_info:
                    Autologtuple(
                        (case_path, ) + crit_ ,
                        sheet_dir["sheet_1"],
                        worksheet_name=sheets["ac"],
                        creds_file=creds_path
                    )
            
        except Exception as e:
            print("".join(traceback.format_exc()))
            print(f"Error processing case {case_path}: {str(e)}")

if __name__ == "__main__":
    # Let's make it parameterized 
    main()
