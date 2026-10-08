import pandas as pd

# List all source file paths
source_files = [
    f"autopipeline-benchmarks/github-pipelines/length9_36/training_{i}.csv" for i in range(135)
]

# Read all source tables into a list of DataFrames
dfs = [pd.read_csv(fp, index_col=0) for fp in source_files]

# UNION all source tables by concatenation
union_df = pd.concat(dfs, ignore_index=True)

# GROUP BY 'name' and 'sex', aggregate sum on 'number'
result_df = union_df.groupby(['name', 'sex'], as_index=False).agg({'number': 'sum'})

# Write the final output
result_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_36/target_multisource_mcts.csv", index=False)