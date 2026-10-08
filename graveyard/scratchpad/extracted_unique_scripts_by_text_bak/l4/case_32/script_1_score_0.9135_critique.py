import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)

# Rename r1403 columns in df0 and df4 to match target schema
df0 = df0.rename(columns={"r1403": "r1403_x"})
df4 = df4.rename(columns={"r1403": "r1403_y"})

# Join df3 and df2 on County
join1 = pd.merge(df3, df2, on="County", how="inner")

# Join with df0 (r1403_x)
join2 = pd.merge(join1, df0, on="County", how="inner")

# Join with df4 (r1403_y)
join3 = pd.merge(join2, df4, on="County", how="inner")

# Join with df1 (only County column)
final_join = pd.merge(join3, df1, on="County", how="inner")

# Group by County to ensure uniqueness, no aggregation needed
result = final_join.groupby("County", dropna=False).first().reset_index()

# Reorder columns to match target schema exactly
result = result[["County", "r1401", "r1402", "r1403_x", "r1403_y"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv", index=False)