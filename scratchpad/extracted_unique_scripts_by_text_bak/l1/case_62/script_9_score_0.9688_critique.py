import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)
df0 = df0.rename(columns={"Text Date": "Month"})
df0 = df0[["Month", "Water Use", "Power Use"]]

# Convert types explicitly
df0["Water Use"] = df0["Water Use"].astype(float)
df0["Power Use"] = df0["Power Use"].astype(int)

# Group by Month and sum the numeric columns
df_grouped = df0.groupby("Month", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})

# Ensure Power Use is integer type after aggregation
df_grouped["Power Use"] = df_grouped["Power Use"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts.csv", index=False)