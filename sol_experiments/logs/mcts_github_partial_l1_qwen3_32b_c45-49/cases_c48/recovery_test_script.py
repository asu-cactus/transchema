import pandas as pd

# Load the source data, skipping the index column
df = pd.read_csv(
    "autopipeline-benchmarks/github-pipelines/length1_48/test_0.csv",
    index_col=0
)

# Filter and rename relevant columns
df = df[["Text Date", "Water Use", "Power Use"]]
df = df.rename(columns={"Text Date": "Date"})

# Group by Date and sum Water Use and Power Use to match target schema
df_grouped = df.groupby("Date", as_index=False).sum()

# Save the transformed data
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts_recovery_test_val.csv", index=False)