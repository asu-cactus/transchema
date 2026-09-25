import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

# Convert 'Split' and 'Subject' to categorical codes before concatenation
for df in [df0, df1, df2, df3]:
    df['Split'] = df['Split'].astype('category').cat.codes.astype(int)
    df['Subject'] = df['Subject'].astype('category').cat.codes.astype(int)

# Concatenate all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by the three keys and sum the numeric columns
agg = df_all.groupby(['SubjectId', 'Split', 'Subject'], as_index=False).agg({
    'PA': 'sum',
    'AB': 'sum',
    'H': 'sum',
    'TB': 'sum',
    'BB': 'sum',
    'SF': 'sum',
    'HBP': 'sum'
})

# Ensure all columns are integer type as per target schema
agg = agg.astype({
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

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)