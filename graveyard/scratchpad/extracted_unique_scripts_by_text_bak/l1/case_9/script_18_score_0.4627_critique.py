import pandas as pd

# List all source CSV files (assuming 5 source files as example)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_9/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_9/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_9/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_9/training_4.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df = pd.concat(dfs, ignore_index=True)

# Group by zipcode and AGI_STUB, aggregate sum on N1 and A00100
result = df.groupby(['zipcode', 'AGI_STUB'], as_index=False).agg({'N1': 'sum', 'A00100': 'sum'})

# Ensure correct dtypes as per target schema
result = result.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)