import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on='Value Date', suffixes=('_left', '_right'))

df_pivot = df_joined[['Value Date', 'Water Use_left', 'Power Use_right']].copy()
df_pivot.rename(columns={'Value Date': 'Date', 'Water Use_left': 'Water Use', 'Power Use_right': 'Power Use'}, inplace=True)

df_pivot['Date'] = df_pivot['Date'].astype(str)
df_pivot['Water Use'] = df_pivot['Water Use'].astype(float)
df_pivot['Power Use'] = df_pivot['Power Use'].astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)