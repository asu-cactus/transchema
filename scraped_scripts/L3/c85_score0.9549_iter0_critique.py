import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_0.csv", index_col=0)  # County, m1403
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_1.csv", index_col=0)  # County, m1402 (not used)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_2.csv", index_col=0)  # County, m1401
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_3.csv", index_col=0)  # County

# Join df2 and df0 on County to get m1401 and m1403
df_merged = pd.merge(df2, df0, on="County", how="inner")

# Join with df3 to filter counties to those present in df3
df_final = pd.merge(df_merged, df3, on="County", how="inner")

# Select only columns in target schema
df_final = df_final[["County", "m1401", "m1403"]]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_85/target_multisource_mcts.csv", index=False)