import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert 'Split' and 'Subject' columns to consistent integer codes
# Factorize assigns unique integer codes to each unique string, starting from 0
df['Split'] = pd.factorize(df['Split'])[0]
df['Subject'] = pd.factorize(df['Subject'])[0]

# Ensure 'SubjectId' is integer
df['SubjectId'] = pd.to_numeric(df['SubjectId'], errors='coerce').astype('Int64')

# Convert all numeric columns to numeric dtype
for col in ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# Group by key columns and sum the numeric columns
df_grouped = df.groupby(['SubjectId', 'Split', 'Subject'], as_index=False).agg({
    'PA': 'sum',
    'AB': 'sum',
    'H': 'sum',
    'TB': 'sum',
    'BB': 'sum',
    'SF': 'sum',
    'HBP': 'sum'
})

# Reorder columns to match target schema exactly
df_grouped = df_grouped[['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

# Write to output CSV
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)