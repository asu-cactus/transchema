import pandas as pd

# Read the single source table (only one source given)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

# If there were multiple source tables, we would union them here.
# Since only one source is given, union is trivial.

# Group by 'Text Date' and sum the numeric columns
agg_df = df0.groupby("Text Date", as_index=False).agg({
    "Water Use": "sum",
    "Power Use": "sum"
})

# Convert types to match target schema
agg_df["Water Use"] = agg_df["Water Use"].astype(float)
agg_df["Power Use"] = agg_df["Power Use"].round().astype(int)

# Rename 'Text Date' to 'Date'
agg_df = agg_df.rename(columns={"Text Date": "Date"})

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)