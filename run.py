import argparse
import logging

from experiment import Experiment


def parse_args():
    args = argparse.ArgumentParser()
    # data
    args.add_argument('--data_path', type=str, default='./data/chatgpt.json')
    args.add_argument('--source_start_idx', type=int, default=0)
    args.add_argument('--max_pipeline_len_idx', type=int, default=1)
    args.add_argument('--pipeline_len_start_idx', type=int, default=1)
    args.add_argument('--target_start_idx', type=int, default=0)
    args.add_argument('--max_target_idx', type=int, default=99)
    args.add_argument('--max_attempts', type=int, default=5)

    # Agent
    args.add_argument('--clarity_on', type=bool, default=False)
    args.add_argument('--method', type=str, choices=['monolithic', 'mcts', 'cot'], default='monolithic')
    # Search
    # MCTS

    args.add_argument('--backend', type=str,
                      choices=['gpt-3.5-turbo-16k', 'gpt-4-1106-preview', 'gpt-4-0125-preview'],
                      default='gpt-4-0125-preview')
    args.add_argument('--temperature', type=float, default=0)

    # 1000
    args.add_argument('--prompt_sample', type=str, choices=['standard', 'cot'], default='cot')
    args.add_argument('--n_generate_sample', type=int, default=1)
    args.add_argument('--n_evaluate_sample', type=int, default=1)
    args.add_argument('--iterations', type=int, default=30)
    # Others
    args.add_argument('--log_dir', type=str, default='logs/')

    args = args.parse_args()
    args = vars(args)
    return args


def main(args):
    experiment = Experiment(**args)
    experiment.setup()
    # experiment.get_llm_friendly_representation()
    logging.info(f"STARTING experiment: \n{experiment}")
    try:
        experiment.run()
    except Exception as e:
        logging.error(f"Error during experiment run: {e}")
    finally:
        # Always log the cost, even if an error occurred
        logging.info(f"COST of this experiment: \n{experiment.token_tracker.cost_summary()}")
        # experiment.teardown()



if __name__ == "__main__":
    args = parse_args()
    main(args)
