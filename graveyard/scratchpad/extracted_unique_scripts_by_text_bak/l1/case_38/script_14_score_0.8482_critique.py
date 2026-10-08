import pandas as pd

# Read source table
source = pd.read_csv(
    "autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv",
    index_col=0
)

# Group by user_id and aggregate mean of sad.depressed and open.stressed
result = source.groupby("user_id", as_index=False).agg({
    "sad.depressed": "mean",
    "open.stressed": "mean"
})

# Rename columns to match target schema
result = result.rename(columns={
    "sad.depressed": "sad",
    "open.stressed": "stressed"
})

# Write output
result.to_csv(
    "autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv",
    index=False
)