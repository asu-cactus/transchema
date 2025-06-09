from methods.multi_step import multi_step
from methods.intermediate_materialization import intermediate_materialization


def precursor(args, length, id_, log_dir_, experiment_name, i_):
    if args.intermediate_materialization_flag == 1:
        # intermediate materialization
        return intermediate_materialization(
            args, length, id_, log_dir_, experiment_name, i_
        )
    else:
        # multi step
        return multi_step(args, length, id_, log_dir_, experiment_name, i_)
