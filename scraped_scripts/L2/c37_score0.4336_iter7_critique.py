import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_37/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_37/training_1.csv", index_col=0)

# Outer join on Date to keep all dates from both sources
merged = pd.merge(df0, df1, on="Date", how="outer")

# Fill missing NumMosquitos with 0 before aggregation
merged["NumMosquitos"] = merged["NumMosquitos"].fillna(0)

# Group by Date and sum NumMosquitos
result = merged.groupby("Date", as_index=False)["NumMosquitos"].sum()

# Ensure correct types
result["Date"] = result["Date"].astype(str)
result["NumMosquitos"] = result["NumMosquitos"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_37/target_multisource_mcts.csv", index=False)