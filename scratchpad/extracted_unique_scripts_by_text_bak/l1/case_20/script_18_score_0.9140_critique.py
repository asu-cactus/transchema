import pandas as pd

# Read the single source table (if multiple sources existed, we would read and union them here)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv", index_col=0)

# Since only one source table is given, UNION is trivial (just df0)
# If there were multiple source tables, we would concatenate them here

# Group by 'sex' and 'smoker' and aggregate by mean for numeric columns
agg_df = df0.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)