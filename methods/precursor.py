from methods.multi_step import multi_step
from methods.intermediate_materialization import intermediate_materialization
import parameters as p

def precursor(length, id_, log_dir_, experiment_name,i_) : 
    if(p.intermediate_materialization_flag == 1):
        # intermediate materialization
        return intermediate_materialization(length, id_, log_dir_, experiment_name,i_)
    else:
        # multi step
        return multi_step(length, id_, log_dir_, experiment_name,i_)