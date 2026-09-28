import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv", index_col=0).rename(columns={'0': '0_x'})
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv", index_col=0).rename(columns={'0': '0_y'})

df_merged = df0.merge(df1, left_on='right_index', right_index=True, how='inner')

result = df_merged[['0_x', '0_y']].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv", index=False)