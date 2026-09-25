import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)
df_result = df_union[['CUSTOMERNAME', 'ORDERNUMBER']].copy()
df_result['ORDERNUMBER'] = pd.to_numeric(df_result['ORDERNUMBER'], errors='coerce').astype('Int64')

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)