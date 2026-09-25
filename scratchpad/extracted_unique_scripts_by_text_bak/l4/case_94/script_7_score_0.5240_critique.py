import pandas as pd

# Read all source CSVs
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by 'Split' and 'SubjectId' and sum numeric columns
group_cols = ['Split', 'SubjectId']
agg_cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']

result = df_all.groupby(group_cols, as_index=False)[agg_cols].sum()

# Set 'Subject' column equal to 'SubjectId' as integer
result['Subject'] = result['SubjectId'].astype(int)

# Reorder columns to match target schema
result = result[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

# Ensure correct dtypes
result = result.astype({
    'Split': str,
    'SubjectId': int,
    'Subject': int,
    'PA': int,
    'AB': int,
    'H': int,
    'TB': int,
    'BB': int,
    'SF': int,
    'HBP': int
})

# Write output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)