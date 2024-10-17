import subprocess
from bayes_opt import BayesianOptimization
from bayes_opt.util import UtilityFunction
import random
# run process 
def run_auto_suggest_llm_bayesian(len_id, max_len_id, target_id, max_target_id, target_per, 
                                  is_perc, target_length, source_length, join_flag, 
                                  aggregate_flag, join_hints_truncate, aggregate_hints_truncate, 
                                  fd_flag, token_limit, model):
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

    # Run the script with the given arguments
    subprocess.run(args)

# Example parameter values as described in your request
len_id = 4
max_len_id = 4
target_id = 88
max_target_id = 88
target_per = 25
is_perc = False
target_length = 5
source_length = 7
join_flag = 1
aggregate_flag = 1
join_hints_truncate = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
aggregate_hints_truncate = [0.5, 0.5, 0.5, 0.5]
fd_flag = 1
token_limit = 5000
model = 'gpt-4-turbo'

# Call the function with the above parameters
run_auto_suggest_llm_bayesian(
    len_id, max_len_id, target_id, max_target_id, target_per, 
    is_perc, target_length, source_length, join_flag, 
    aggregate_flag, join_hints_truncate, aggregate_hints_truncate, 
    fd_flag, token_limit, model
)

def evaluate_parameters(training_len, target_samples, source_samples, 
                    distinct_value_ratio, value_overlap_js, value_overlap_jc, value_range_overlap, leftness_join, sortedness, 
                    distinct_value_count, leftness_group_by, emptiness, peak_frequency, 
                    fd) : 
    
    len_id = training_len
    max_len_id = training_len
    target_id = random.randint(2,99)
    max_target_id = target_id
    target_per = 25
    is_perc = False
    target_length = int(max(3,target_samples*50))
    source_length = int(max(3,source_samples*10))
    join_flag = 1
    aggregate_flag = 1
    join_hints_truncate = [distinct_value_ratio, value_overlap_js, value_overlap_jc, value_range_overlap, leftness_join, sortedness]
    aggregate_hints_truncate = [distinct_value_count, leftness_group_by, emptiness, peak_frequency]
    fd_flag = 1
    token_limit = 5000
    model = 'gpt-4-turbo'

    run_auto_suggest_llm_bayesian(
        len_id, max_len_id, target_id, max_target_id, target_per, 
        is_perc, target_length, source_length, join_flag, 
        aggregate_flag, join_hints_truncate, aggregate_hints_truncate, 
        fd_flag, token_limit, model
    )

    
    



def optimization(pbounds, training_len) : 
    optimizer = BayesianOptimization(
        f = lambda target_samples, source_samples, \
                    distinct_value_ratio, value_overlap_js, value_overlap_jc, value_range_overlap, leftness_join, sortedness, \
                    distinct_value_count, leftness_group_by, emptiness, peak_frequency, \
                    fd : evaluate_parameters(training_len, target_samples, source_samples, 
                    distinct_value_ratio, value_overlap_js, value_overlap_jc , value_range_overlap, leftness_join, sortedness, 
                    distinct_value_count, leftness_group_by, emptiness, peak_frequency, 
                    fd),
                    pbounds = pbounds,
                    verbose=2,
                    random_state = 1
        )
    

    optimizer.set_gp_params(normalize_y=True)

    utility = UtilityFunction(kind="ei", kappa=2.5, xi=0.0)

    optimizer.maximize(
        init_points=1,
        n_iter=5,
        acquisition_function=utility
    )

    best_params = optimizer.max['params']
    print("Best Parameters:", best_params)

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
        'sortedness' : (0,1)
        # aggregate
        'distinct_value_count' : (0,1),
        'leftness_group_by' : (0,1),
        'emptiness' : (0,1),
        'peak_frequency' : (0,1),
        #functional_dependency
        'fd' : (0,1)
    }

    training_len = 4
    exceptions = []

    optimization(pbounds = pbounds, training_len = training_len)


# score calculation 


# 