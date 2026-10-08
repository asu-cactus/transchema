import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)

df0 = df0.rename(columns={'Text Date': 'Month'})

df_final = df0.groupby('Month', as_index=False).agg({'Water Use': 'sum', 'Power Use': 'sum'})

df_final['Water Use'] = df_final['Water Use'].astype(float)
df_final['Power Use'] = df_final['Power Use'].astype(int)

df_final = df_final[['Month', 'Water Use', 'Power Use']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts.csv", index=False)