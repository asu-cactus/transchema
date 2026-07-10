import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)

pivoted = df0.groupby('crit_cn')['critic'].sum().reset_index()

pivoted['critic'] = pivoted['critic'].astype(int)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)