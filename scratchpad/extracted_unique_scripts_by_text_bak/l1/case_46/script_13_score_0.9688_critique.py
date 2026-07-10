import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

# Rename "Text Date" to "Date"
df0 = df0.rename(columns={"Text Date": "Date"})

# Drop columns not needed in target
df0 = df0[["Date", "Water Use", "Power Use"]]

# Group by Date and sum Water Use and Power Use
df0_grouped = df0.groupby("Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})

# Cast types to match target schema
df0_grouped["Water Use"] = df0_grouped["Water Use"].astype(float)
df0_grouped["Power Use"] = df0_grouped["Power Use"].astype(int)

# Sort by Date to match target examples order
df0_grouped = df0_grouped.sort_values("Date")

# Write output
df0_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)