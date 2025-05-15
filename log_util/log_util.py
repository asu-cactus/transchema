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