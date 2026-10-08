import pandas as pd

# Read the single source table
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

# Group by PRECINCT and sum all relevant columns
result = df.groupby('PRECINCT', dropna=False).agg({
    'ELIGIBLE_VOTERS': 'sum',
    'POLLS': 'sum',
    'EARLY_VOING': 'sum',
    'ABSENTEE': 'sum',
    'PROVISIONAL': 'sum'
}).reset_index()

# Convert columns to integer as per target schema
result['ELIGIBLE_VOTERS'] = result['ELIGIBLE_VOTERS'].astype(int)
result['POLLS'] = result['POLLS'].astype(int)
result['EARLY_VOING'] = result['EARLY_VOING'].astype(int)
result['ABSENTEE'] = result['ABSENTEE'].astype(int)
result['PROVISIONAL'] = result['PROVISIONAL'].astype(int)

# Write to target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)