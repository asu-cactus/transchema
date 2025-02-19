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
                    distinct_value_ratio, value_overlap_js, value_overlap_jc, value_range_overlap, leftness_join, sortedness, 
                    distinct_value_count, leftness_group_by, emptiness, peak_frequency, 
                    fd, logger) : 
    
    # Nodes in Cluster
    lengths = [
    "length1_4", "length1_42", "length2_42", "length4_39", "length4_40", 
    "length4_41", "length4_45", "length4_56", "length4_58", "length4_65", 
    "length4_84", "length5_14", "length5_21", "length5_26", "length5_28", 
    "length5_35", "length5_40", "length5_46", "length5_50", "length5_64", 
    "length5_67", "length5_9", "length5_93", "length5_97", "length6_11", 
    "length6_31", "length6_36", "length6_45", "length6_51", "length6_52", 
    "length6_66", "length6_67", "length6_8", "length6_89", "length6_91", 
    "length6_95", "length6_97", "length9_19", "length9_22", "length9_29", 
    "length9_35", "length9_49"
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
    aggregate_hints_truncate = [distinct_value_count, leftness_group_by, emptiness, peak_frequency]
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


def optimization(pbounds, training_len, logger) : 
    optimizer = BayesianOptimization(
        f = lambda target_samples, source_samples, \
                    distinct_value_ratio, value_overlap_js, value_overlap_jc, value_range_overlap, leftness_join, sortedness, \
                    distinct_value_count, leftness_group_by, emptiness, peak_frequency, \
                    fd : evaluate_parameters(training_len, target_samples, source_samples, 
                    distinct_value_ratio, value_overlap_js, value_overlap_jc , value_range_overlap, leftness_join, sortedness, 
                    distinct_value_count, leftness_group_by, emptiness, peak_frequency, 
                    fd, logger),
                    pbounds = pbounds,
                    verbose=2,
                    random_state = 1
        )
    

    optimizer.set_gp_params(normalize_y=True)

    utility = UtilityFunction(kind="ei", kappa=2.5, xi=0.0)

    optimizer.maximize(
        init_points=3,
        n_iter=20,
        acquisition_function=utility
    )

    best_params = optimizer.max['params']
    print("Best Parameters:", best_params)
    logger.log("Best Parameters : ", best_params)

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
        'distinct_value_count' : (0,1),
        'leftness_group_by' : (0,1),
        'emptiness' : (0,1),
        'peak_frequency' : (0,1),
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
    log_file = f"bayesian_opt_cluster_0{current_time}.log"

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