import pandas as pd

# List all source files (assuming 10 source files named training_0.csv to training_9.csv)
source_files = [
    f"autopipeline-benchmarks/github-pipelines/length1_99/training_{i}.csv" for i in range(10)
]

# Read all source tables into a list of dataframes
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Concatenate all source tables (UNION)
df = pd.concat(dfs, ignore_index=True)

# Cast columns to correct types as per target schema
df = df.astype({
    'user_id': 'int64',
    'timestamp': 'string',
    'source': 'string',
    'device': 'string',
    'operative_system': 'string',
    'test': 'int64',
    'price': 'int64',
    'converted': 'int64'
})

# Write to target file
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_99/target_multisource_mcts.csv", index=False)