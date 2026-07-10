import pandas as pd

# Read the single source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

# If multiple source tables existed, we would union them here.
# Since only one source table is given, union is trivial.
df = df0.copy()

# Group by PRECINCT and sum the numeric columns
result = df.groupby('PRECINCT', as_index=False).agg({
    'ELIGIBLE_VOTERS': 'sum',
    'POLLS': 'sum',
    'EARLY_VOING': 'sum',
    'ABSENTEE': 'sum',
    'PROVISIONAL': 'sum'
})

# Convert columns to integer type as in target schema
result['ELIGIBLE_VOTERS'] = result['ELIGIBLE_VOTERS'].astype(int)
result['POLLS'] = result['POLLS'].astype(int)
result['EARLY_VOING'] = result['EARLY_VOING'].astype(int)
result['ABSENTEE'] = result['ABSENTEE'].astype(int)
result['PROVISIONAL'] = result['PROVISIONAL'].astype(int)

# Write to target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)