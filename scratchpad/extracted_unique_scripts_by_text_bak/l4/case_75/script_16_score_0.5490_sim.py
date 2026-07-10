import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)

df_target = df0[['type', 'size', 'budget']].copy()
df_target.rename(columns={'size': 'a', 'budget': 'b'}, inplace=True)
df_target['a'] = df_target['a'].astype(float)
df_target['b'] = df_target['b'].astype(float)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)