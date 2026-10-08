import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
target = source0[['customer_id', 'date']].copy()
target['customer_id'] = target['customer_id'].astype(int)
target['date'] = target['date'].astype(str)
target.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)