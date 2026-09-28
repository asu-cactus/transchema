import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_35/training_1.csv", index_col=0)

df0['ResultDir'] = pd.to_numeric(df0['ResultDir'], errors='coerce')
df1['NumMosquitos'] = pd.to_numeric(df1['NumMosquitos'], errors='coerce')

grouped_source0 = df0.groupby('Date', as_index=False)['ResultDir'].mean()
grouped_source1 = df1.groupby('Date', as_index=False)['NumMosquitos'].mean()

merged = pd.merge(grouped_source0, grouped_source1, on='Date', how='inner')

merged['Date'] = merged['Date'].astype(str)
merged['ResultDir'] = merged['ResultDir'].astype(float)
merged['NumMosquitos'] = merged['NumMosquitos'].astype(float)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_35/target_multisource_mcts.csv", index=False)