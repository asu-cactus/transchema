import pandas as pd

# Read the single source table (if multiple, read all and union)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

# Since only one source table is given, union is trivial
df_union = df0.copy()

# Group by "Text Date" and aggregate mean of Water Use and Power Use
agg = df_union.groupby("Text Date").agg({"Water Use": "mean", "Power Use": "mean"}).reset_index()

# Rename "Text Date" to "Date"
agg.rename(columns={"Text Date": "Date"}, inplace=True)

# Cast columns to match target schema
agg["Water Use"] = agg["Water Use"].astype(float)
agg["Power Use"] = agg["Power Use"].round().astype(int)

# Select columns in target schema order
result = agg[["Date", "Water Use", "Power Use"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)