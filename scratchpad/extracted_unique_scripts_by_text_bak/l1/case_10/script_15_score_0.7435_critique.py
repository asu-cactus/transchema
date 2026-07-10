import pandas as pd

# Read source table
source_path = "autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

# Group by PRECINCT and sum the numeric columns
result = df.groupby('PRECINCT', as_index=False).agg({
    'ELIGIBLE_VOTERS': 'sum',
    'POLLS': 'sum',
    'EARLY_VOING': 'sum',
    'ABSENTEE': 'sum',
    'PROVISIONAL': 'sum'
})

# Convert columns to integer type as in target schema
for col in ['ELIGIBLE_VOTERS', 'POLLS', 'EARLY_VOING', 'ABSENTEE', 'PROVISIONAL']:
    result[col] = result[col].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)