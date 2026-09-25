import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)

# Join Source4_32_0 and Source4_32_4 on County to get r1403_x and r1403_y separately
df_r1403 = pd.merge(df0, df4, on="County", how="inner", suffixes=('_x', '_y'))

# Join with df3 (r1401)
df_join1 = pd.merge(df_r1403, df3, on="County", how="inner")

# Join with df2 (r1402)
df_join2 = pd.merge(df_join1, df2, on="County", how="inner")

# Join with df1 (County only)
result = pd.merge(df_join2, df1, on="County", how="inner")

# Select and reorder columns to match target schema
result = result[["County", "r1401", "r1402", "r1403_x", "r1403_y"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv", index=False)