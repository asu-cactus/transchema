import pandas as pd

# List all source files (assuming 5 source files as the target has 5 rows)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_53/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_4.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by continent and aggregate by mean
result = df_all.groupby('continent', as_index=False).agg({
    'beer_servings': 'mean',
    'spirit_servings': 'mean',
    'wine_servings': 'mean',
    'total_litres_of_pure_alcohol': 'mean'
})

# Reorder columns to match target schema exactly
result = result[['continent', 'beer_servings', 'spirit_servings', 'wine_servings', 'total_litres_of_pure_alcohol']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts.csv", index=False)