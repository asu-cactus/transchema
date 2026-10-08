import pandas as pd
import glob

# Read all source files with common schema
sources = []
for i in range(78, 222):  # Covers Source78 to Source221
    pattern = f'autopipeline-benchmarks/github-pipelines/length9_45/training_{i}.csv'
    files = glob.glob(pattern)
    for file in files:
        df = pd.read_csv(file, index_col=0)
        sources.append(df)

# Perform UNION of all source tables
result = pd.concat(sources, ignore_index=True)

# Write to target file
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_45/target_multisource_mcts_recovery_test_val.csv')