import logging 
from datetime import datetime
import os

def create_logger(
    type_, log_dir, pipeline_len_start_idx, target_start_idx, max_target_idx
):
    # Get current system time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the log file name with the current time
    # change here 
    log_file = (
        f"{pipeline_len_start_idx}_target{target_start_idx}_{type_}_{current_time}.log"
    )

    # Check if the log directory exists, create it if it does not
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Setup logging
    logging.basicConfig(
        filename=os.path.join(log_dir, log_file),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="a+",
    )
    return logging.getLogger()

import os
from datetime import datetime

def setup_logging(log_dir, experiment_name):
    # Check if the log directory exists, create it if it does not
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # create an experiment_date_time directory inside the log_directory
    experiment_date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_date_time = os.path.join(log_dir, experiment_name + "_" + experiment_date_time)
    os.makedirs(experiment_date_time)

    # create a log directory inside the experiment_date_time directory
    log_dir = os.path.join(experiment_date_time, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # create a results directory inside the experiment_date_time directory
    results_dir = os.path.join(experiment_date_time, "results")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Create the four CSV files with their headers
    multi_step_path = os.path.join(results_dir, "multi_step.csv")
    with open(multi_step_path, 'w') as f:
        f.write("Length,Hard Match,Soft Match,Soft Acc,Cost,Latency,Score\n")
    
    average_multi_step_path = os.path.join(results_dir, "average_multi_step.csv")
    with open(average_multi_step_path, 'w') as f:
        f.write("Length,Hard Match,Cost,Latency,Soft Match,Soft Acc,Cost_,Latency_\n")
    
    critique_path = os.path.join(results_dir, "critique.csv")
    with open(critique_path, 'w') as f:
        f.write("Length,Critique Type,Hard Match,Soft Match,Soft Acc,Cost,Latency,Score\n")
    
    average_critique_path = os.path.join(results_dir, "average_critique.csv")
    with open(average_critique_path, 'w') as f:
        f.write("Length,Critique Type,Hard Match,Cost,Latency,Soft Match,Soft Acc,Cost_,Latency_,max\n")

    # return path of experiment_date_time directory and subdirectories
    return experiment_date_time, log_dir, results_dir