import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

# Concatenate all sources
df = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Convert 'Subject' and 'Split' columns to categorical codes (integers)
df['Subject'] = df['Subject'].astype('category').cat.codes
df['Split'] = df['Split'].astype('category').cat.codes

# Group by the key columns and sum the stats columns
group_cols = ['SubjectId', 'Split', 'Subject']
agg_cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']

final = df.groupby(group_cols, as_index=False)[agg_cols].sum()

# Ensure all columns are integer type as per target schema
final = final.astype({
    'SubjectId': int,
    'Split': int,
    'Subject': int,
    'PA': int,
    'AB': int,
    'H': int,
    'TB': int,
    'BB': int,
    'SF': int,
    'HBP': int
})

# Write to output CSV
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)