from methods.multi_step import multi_step
from methods.intermediate_materialization import intermediate_materialization
from methods.tree_of_thoughts import tree_of_thoughts


def precursor(args, length, id_, log_dir, experiment_name, i_):
    if args.tree_of_thoughts:
        return tree_of_thoughts(args, length, id_, log_dir)
    elif args.intermediate_materialization:
        # intermediate materialization
        return intermediate_materialization(args, length, id_, log_dir)
    else:
        # multi step
        return multi_step(args, length, id_, log_dir, experiment_name, i_)
