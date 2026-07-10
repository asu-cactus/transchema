import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv", index_col=0)
df_target = df[['zipcode', 'AGI_STUB', 'N1', 'A00100']].copy()
df_target = df_target.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)