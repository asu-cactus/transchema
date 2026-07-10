import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_89/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_89/training_1.csv", index_col=0)

df0_sub = df0[['city', 'fare']]

df1_sub = df1[['city', 'type']]

df1_pivot = df1_sub.pivot_table(index='city', columns='type', aggfunc='size', fill_value=0).reset_index()

df_merged = pd.merge(df0_sub, df1_pivot, on='city', how='outer')

df_result = df_merged[['city', 'fare']]

df_result['fare'] = pd.to_numeric(df_result['fare'], errors='coerce')

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length2_89/target_multisource_mcts.csv", index=False)