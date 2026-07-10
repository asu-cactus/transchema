import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_60/training_0.csv", index_col=0)

pivoted = df0.pivot_table(index='type', values='driver_count', aggfunc='sum').reset_index()

pivoted['driver_count'] = pivoted['driver_count'].astype(int)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)