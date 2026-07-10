import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_37/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_37/training_1.csv", index_col=0)

# Join on 'Date'
df_joined = pd.merge(df0, df1, on="Date", how="inner")

# Group by 'Date' and sum 'NumMosquitos'
result = df_joined.groupby("Date", as_index=False)["NumMosquitos"].sum()

# Ensure correct types
result["NumMosquitos"] = result["NumMosquitos"].astype(int)

# Select only target columns
result = result[["Date", "NumMosquitos"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_37/target_multisource_mcts.csv", index=False)