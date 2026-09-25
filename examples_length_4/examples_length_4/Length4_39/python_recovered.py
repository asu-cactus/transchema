import pandas as pd
import numpy as np

# Define source file paths
source_files = [
    'autopipeline-benchmarks/github-pipelines/length4_39/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_39/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_39/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_39/test_3.csv'
]

dfs = []
for file_path in source_files:
    # Read each source CSV with index_col=0 to ignore the first numerical index column
    df = pd.read_csv(file_path, index_col=0)
    
    # Reorder columns from ['x', 'y', 'label'] to ['label', 'x', 'y'] as target schema
    df = df[['label', 'x', 'y']]
    
    # Round 'x' and 'y' to nearest integer to match target schema
    df['x'] = df['x'].round().astype(int)
    df['y'] = df['y'].round().astype(int)
    
    # Ensure 'label' column is string dtype
    df['label'] = df['label'].astype(str)
    
    dfs.append(df)

# Concatenate all source tables vertically (Union)
target_df = pd.concat(dfs, ignore_index=True)

# Save to target path
target_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_39/target_multisource_cot.csv', index=False)