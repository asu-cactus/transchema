import pandas as pd

# Read all source files (assuming 5 source files as implied by target number of tuples)
# The problem only explicitly shows Source1_53_0, but instructions say all source tables must be used.
# We assume the other source files are named similarly with suffixes _1, _2, _3, _4.

source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_53/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_4.csv"
]

dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# UNION all source tables by concatenation
df_all = pd.concat(dfs, ignore_index=True)

# Group by continent and aggregate by mean for the numeric columns
result = df_all.groupby("continent", as_index=False).agg({
    "beer_servings": "mean",
    "spirit_servings": "mean",
    "wine_servings": "mean",
    "total_litres_of_pure_alcohol": "mean"
})

# Write output with exact target schema and column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts.csv", index=False)