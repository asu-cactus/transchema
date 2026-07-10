import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)
df_result = df_union[['Product', 'Price']].copy()
df_result['Product'] = df_result['Product'].astype(str)
df_result['Price'] = df_result['Price'].astype(float)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)