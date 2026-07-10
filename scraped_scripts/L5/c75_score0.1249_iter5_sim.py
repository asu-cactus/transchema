import pandas as pd

source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_2.csv", index_col=0)

union_df = pd.concat([source1, source2], ignore_index=True, sort=False)

union_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_75/target_multisource_mcts.csv", index=False)