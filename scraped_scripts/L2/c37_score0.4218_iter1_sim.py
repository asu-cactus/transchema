import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_37/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_37/training_1.csv", index_col=0)

df0_sub = df0[['Date']].copy()
df0_sub['NumMosquitos'] = 0
df0_sub['NumMosquitos'] = df0_sub['NumMosquitos'].astype(int)

df1_sub = df1[['Date', 'NumMosquitos']].copy()
df1_sub['NumMosquitos'] = df1_sub['NumMosquitos'].astype(int)

df = pd.concat([df0_sub, df1_sub], ignore_index=True)

df = df[['Date', 'NumMosquitos']]
df['Date'] = df['Date'].astype(str)
df['NumMosquitos'] = df['NumMosquitos'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_37/target_multisource_mcts.csv", index=False)