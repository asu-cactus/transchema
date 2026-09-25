import pandas as pd

# Read all source tables (assuming 5 source files as per naming pattern)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_53/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_4.csv"
]

dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# UNION all source tables (concatenate)
df_all = pd.concat(dfs, ignore_index=True)

# GROUP BY continent and compute average of numeric columns
result = df_all.groupby("continent", as_index=False).agg({
    "beer_servings": "mean",
    "spirit_servings": "mean",
    "wine_servings": "mean",
    "total_litres_of_pure_alcohol": "mean"
})

# Write output with exact target schema and column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts.csv", index=False)