import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
union_all = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Group by the leftmost columns and sum the numeric columns
result = union_all.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA': 'sum',
    'AB': 'sum',
    'H': 'sum',
    'TB': 'sum',
    'BB': 'sum',
    'SF': 'sum',
    'HBP': 'sum'
})

# Ensure the target schema column order and types
# Target schema: ['Split': string, 'SubjectId': integer, 'Subject': integer, 'PA': integer, 'AB': integer, 'H': integer, 'TB': integer, 'BB': integer, 'SF': integer, 'HBP': integer]
# Convert types accordingly
result['Split'] = result['Split'].astype(str)
result['SubjectId'] = result['SubjectId'].astype(int)
result['Subject'] = result['Subject'].astype(int)
for col in ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
    result[col] = result[col].astype(int)

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)