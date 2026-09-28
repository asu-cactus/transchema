import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_98/training_1.csv", index_col=0)

# Join on 'CLUES'
df_joined = pd.merge(df0, df1, on="CLUES", how="inner")

# Group by 'MOTATE_V' and sum 'count'
result = df_joined.groupby("MOTATE_V", as_index=False)["count"].sum()

# Ensure correct types
result["MOTATE_V"] = result["MOTATE_V"].astype(str)
result["count"] = result["count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_98/target_multisource_mcts.csv", index=False)