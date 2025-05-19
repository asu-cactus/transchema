import subprocess
from bayes_opt import BayesianOptimization
from bayes_opt.util import UtilityFunction
import random
import sys
import pandas as pd
from datetime import datetime  
from auto_suggest_llm_util import calculate_score
import os
import logging
# run process 
def run_auto_suggest_llm_bayesian(len_id, max_len_id, target_id, max_target_id, target_per, 
                                  is_perc, target_length, source_length, join_flag, 
                                  aggregate_flag, join_hints_truncate, aggregate_hints_truncate, 
                                  fd_flag, token_limit, model, logger):
    # Convert list arguments to strings
    join_hints_truncate_str = ','.join(map(str, join_hints_truncate))
    aggregate_hints_truncate_str = ','.join(map(str, aggregate_hints_truncate))

    # Create the argument list for subprocess
    args = [
        "python3", "auto-suggest-llm-bayesian-parameterised.py",
        str(len_id), str(max_len_id), str(target_id), str(max_target_id),
        str(target_per), str(int(is_perc)), str(target_length), str(source_length),
        str(join_flag), str(aggregate_flag), join_hints_truncate_str,
        aggregate_hints_truncate_str, str(fd_flag), str(token_limit), model
    ]

    print(args)
    logger.info(args)

    # Run the script with the given arguments
    subprocess.run(args)

# Example parameter values as described in your request
# len_id = 2
# max_len_id = 2
# target_id = 15
# max_target_id = 15
# target_per = 25
# is_perc = False
# target_length = 5
# source_length = 7
# join_flag = 1
# aggregate_flag = 1
# join_hints_truncate = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
# aggregate_hints_truncate = [0.5, 0.5, 0.5, 0.5]
# fd_flag = 1
# token_limit = 120000
# model = 'gpt-4-turbo'

# Call the function with the above parameters
# run_auto_suggest_llm_bayesian(
#     len_id, max_len_id, target_id, max_target_id, target_per, 
#     is_perc, target_length, source_length, join_flag, 
#     aggregate_flag, join_hints_truncate, aggregate_hints_truncate, 
#     fd_flag, token_limit, model
# )

def evaluate_parameters(training_len, target_samples, source_samples, 
                        distinct_value_ratio, value_overlap_js, value_overlap_jc, value_range_overlap, 
                        leftness_join, sortedness, distinct_value_ratio_ub, distinct_value_ratio_lb, 
                        leftness_group_by_ub, leftness_group_by_lb, emptiness_ub, emptiness_lb, 
                        peak_frequency_ub, peak_frequency_lb, value_range_ub, value_range_lb, fd, logger):
    
    # Nodes in Cluster
    lengths = [ 
    "length1_11", "length2_76", "length5_44", "length5_85", "length2_84", "length2_79",
    "length5_83", "length3_43", "length2_20", "length3_30", "length2_61", "length1_93",
    "length2_70", "length4_18", "length4_21", "length3_20", "length2_85", "length2_74",
    "length1_67", "length1_3", "length2_13", "length2_88", "length5_30", "length1_62",
    "length2_1", "length2_64", "length4_9", "length2_17", "length5_1", "length5_89",
    "length2_41", "length5_12", "length3_40", "length3_39", "length5_43", "length5_78",
    "length2_80", "length3_22", "length2_33", "length2_39", "length2_8", "length1_38",
    "length1_95", "length5_76", "length2_55", "length3_66", "length1_46", "length1_35",
    "length3_59", "length2_89", "length1_70", "length5_77", "length5_86", "length2_23",
    "length1_29", "length5_74", "length4_85", "length1_68", "length1_80", "length5_96",
    "length3_70", "length1_44", "length1_86", "length5_10", "length5_61", "length1_59",
    "length2_77", "length2_98", "length1_30", "length1_71", "length3_76", "length5_75",
    "length5_36", "length3_64", "length1_0", "length3_9", "length2_32", "length3_71",
    "length5_8", "length1_43", "length2_26", "length2_25", "length4_83", "length3_61",
    "length1_55", "length4_75", "length1_23", "length1_77", "length4_0", "length3_21",
    "length2_62", "length1_65", "length1_57", "length3_4", "length2_40", "length2_92",
    "length3_69", "length2_48", "length2_75", "length2_94", "length2_72", "length2_93",
    "length1_34", "length4_48", "length3_60", "length2_9", "length2_44", "length1_82",
    "length4_72", "length2_58", "length2_30", "length3_35", "length5_88", "length1_16",
    "length5_22", "length5_87", "length2_34", "length2_11", "length5_29", "length2_71",
    "length2_87", "length3_83", "length1_94", "length5_95", "length1_81", "length6_62",
    "length2_68", "length1_69", "length1_61", "length3_74", "length3_57", "length2_38",
    "length1_90", "length2_18", "length2_99", "length4_20", "length1_21", "length2_69",
    "length2_2", "length3_50", "length1_20", "length3_73", "length1_84", "length5_71",
    "length1_97", "length1_98", "length3_65", "length3_75", "length2_83", "length5_13",
    "length4_80", "length1_53", "length1_41", "length1_18", "length3_84", "length4_73",
    "length2_90", "length1_92", "length1_78", "length1_13", "length5_18", "length1_60",
    "length1_40", "length1_6", "length2_81", "length3_93", "length4_81", "length4_7",
    "length2_16", "length1_48", "length4_19", "length2_19", "length4_57", "length2_7",
    "length5_92"
]



    evaluation_case = random.choice(lengths)
    len_id = int(evaluation_case[6])
    max_len_id = len_id
    # target_list = [18,2,32,33,96,16,27,78,91,18]#2:[11,18,22,25,62,10,16,31,38,5]
    target_id = int(evaluation_case[8:])
    max_target_id = target_id
    target_per = 25
    is_perc = False
    target_length = int(max(3,target_samples*10))
    source_length = int(max(3,source_samples*10))
    join_flag = 1
    aggregate_flag = 1
    join_hints_truncate = [distinct_value_ratio, value_overlap_js, value_overlap_jc, value_range_overlap, leftness_join, sortedness]
    aggregate_hints_truncate = [distinct_value_ratio_ub, distinct_value_ratio_lb, leftness_group_by_ub, leftness_group_by_lb, 
                                emptiness_ub, emptiness_lb, peak_frequency_ub, peak_frequency_lb, value_range_ub, value_range_lb]
    fd_flag = (1 if fd > 0.5 else 0)
    token_limit = 120000
    model = 'gpt-4-turbo'

    logger.info("Iteration Started for parameters : ")

    run_auto_suggest_llm_bayesian(
        len_id, max_len_id, target_id, max_target_id, target_per, 
        is_perc, target_length, source_length, join_flag, 
        aggregate_flag, join_hints_truncate, aggregate_hints_truncate, 
        fd_flag, token_limit, model, logger
    )

    #evaluate 

    main_directory = "autopipeline-benchmarks/github-pipelines"
    # read target_df
    ground_truth_location = '{main_directory}/length{len_id}_{target_id}/target.csv'.format(main_directory = main_directory, len_id = str(len_id), target_id = str(target_id))
    gt = pd.read_csv(ground_truth_location, low_memory = False)
    try : 
        gt = gt.drop('Unnamed: 0', axis=1)
    except : 
        pass
    # read generated_df
    generated_df_location = '{main_directory}/length{len_id}_{target_id}/target_multisource_bayesian_training.csv'.format(main_directory = main_directory, len_id = str(len_id), target_id = str(target_id))
    try : 
        tgt = pd.read_csv(generated_df_location, low_memory = False)
    except : 
        logger.info(0)
        return 0
    try : 
        tgt = tgt.drop('Unnamed: 0', axis=1)
    except : 
        pass
    # calculate score 
    try : 
        score = calculate_score(gt,tgt)
    except : 
        score = 0
    logger.info(score)
    
    # return score 
    return score    

    
    
# score = evaluate_parameters(len_id, target_length, source_length,
#                      join_hints_truncate[0], join_hints_truncate[1], join_hints_truncate[2], join_hints_truncate[3],join_hints_truncate[4],join_hints_truncate[5],
#                      aggregate_hints_truncate[0], aggregate_hints_truncate[1], aggregate_hints_truncate[2], aggregate_hints_truncate[3],
#                      fd_flag
#                      )

# print(score)

# sys.exit()


def optimization(pbounds, training_len, logger): 
    optimizer = BayesianOptimization(
        f=lambda target_samples, source_samples, \
                  distinct_value_ratio, value_overlap_js, value_overlap_jc, value_range_overlap, leftness_join, sortedness, \
                  distinct_value_ratio_ub,distinct_value_ratio_lb, leftness_group_by_ub, leftness_group_by_lb, emptiness_ub, emptiness_lb, peak_frequency_ub, peak_frequency_lb, \
                  value_range_ub, value_range_lb, fd: evaluate_parameters(
                      training_len, target_samples, source_samples, 
                      distinct_value_ratio, value_overlap_js, value_overlap_jc, value_range_overlap, leftness_join, sortedness, 
                      distinct_value_ratio_ub,distinct_value_ratio_lb, leftness_group_by_ub, leftness_group_by_lb, emptiness_ub, emptiness_lb, peak_frequency_ub, peak_frequency_lb, 
                      value_range_ub, value_range_lb, fd, logger
                  ),
        pbounds=pbounds,
        verbose=2,
        random_state=1
    )
    
    optimizer.set_gp_params(normalize_y=True)

    utility = UtilityFunction(kind="ei", kappa=2.5, xi=0.1)

    optimizer.maximize(
        init_points=3,
        n_iter=50,
        acquisition_function=utility
    )

    best_params = optimizer.max['params']
    print("Best Parameters:", best_params)
    logger.info("Best Parameters : " + str(best_params))

    return optimizer



if __name__ == '__main__':

    pbounds = {
        'target_samples' : (0,1),
        'source_samples' : (0,1),
        # join
        'distinct_value_ratio' : (0,1),
        'value_overlap_js' : (0,1),
        'value_overlap_jc' : (0,1),
        'value_range_overlap' : (0,1),
        'leftness_join' : (0,1),
        'sortedness' : (0,1),
        # aggregate
        # [dvr_ub,dvr_lb, leftness_ub,leftness_lb, emptiness_ub,emptiness_lb, peak_frequency_ub, peak_frequency_lb,value_range_ub, value_range_lb]
        'distinct_value_ratio_ub' : (0,1),
        'distinct_value_ratio_lb' : (0,1),
        'leftness_group_by_ub' : (0,1),
        'leftness_group_by_lb' : (0,1),
        'emptiness_ub' : (0,1),
        'emptiness_lb' : (0,1),
        'peak_frequency_ub' : (0,1),
        'peak_frequency_lb' : (0,1),
        'value_range_ub' : (0,1),
        'value_range_lb' : (0,1),
        #functional_dependency
        'fd' : (0,1)
    }

    

    training_len = 3
    exceptions = []

    # setup logger
    current_date = datetime.now().strftime("%Y%m%d") 
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = f"bayesian_opt_cluster{current_date}"

    # Create the log file name with the current time
    log_file = f"bayesian_opt_cluster_6{current_time}.log"

    # Check if the log directory exists, create it if it does not
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Setup logging
    logging.basicConfig(filename=os.path.join(log_dir, log_file), level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s', filemode='a+')
    logger = logging.getLogger()

    logger.info("Experiment Started")

    optimization(pbounds = pbounds, training_len = training_len, logger = logger)


# score calculation 


# 