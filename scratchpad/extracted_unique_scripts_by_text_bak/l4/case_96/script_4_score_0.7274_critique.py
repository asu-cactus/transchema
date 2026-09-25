import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert 'Split' and 'Subject' columns to categorical codes (integers)
df_all['Split'] = df_all['Split'].astype('category').cat.codes
df_all['Subject'] = df_all['Subject'].astype('category').cat.codes

# Group by keys and sum numeric columns
grouped = df_all.groupby(['SubjectId', 'Split', 'Subject'], as_index=False).agg({
    'PA': 'sum',
    'AB': 'sum',
    'H': 'sum',
    'TB': 'sum',
    'BB': 'sum',
    'SF': 'sum',
    'HBP': 'sum'
})

# Convert all columns to int as per target schema
for col in ['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
    grouped[col] = grouped[col].astype(int)

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)