import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)

# Join df0 and df4 on County, rename their r1403 columns to r1403_x and r1403_y respectively
df0_renamed = df0.rename(columns={"r1403": "r1403_x"})
df4_renamed = df4.rename(columns={"r1403": "r1403_y"})
join_0_4 = pd.merge(df0_renamed, df4_renamed, on="County", how="outer")

# Join with df1 (only County column)
join_0_4_1 = pd.merge(join_0_4, df1, on="County", how="outer")

# Join with df2 (County, r1402)
join_0_4_1_2 = pd.merge(join_0_4_1, df2, on="County", how="outer")

# Join with df3 (County, r1401)
final_df = pd.merge(join_0_4_1_2, df3, on="County", how="outer")

# Reorder columns to match target schema: ['County', 'r1401', 'r1402', 'r1403_x', 'r1403_y']
final_df = final_df[["County", "r1401", "r1402", "r1403_x", "r1403_y"]]

# Group by County only (unique key), no aggregation needed, just drop duplicates if any
final_df = final_df.groupby("County", as_index=False).first()

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv", index=False)