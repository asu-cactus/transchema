import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_4/training_0.csv", index_col=0)
df_union = df0[['SN', 'Price']].copy()
df_union['SN'] = df_union['SN'].astype(str)
df_union['Price'] = df_union['Price'].astype(float)
df_union.to_csv("autopipeline-benchmarks/github-pipelines/length3_4/target_multisource_mcts.csv", index=False)