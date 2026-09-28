import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Map 'Subject' string column to integer IDs (consistent with target schema)
df_all['Subject'] = pd.factorize(df_all['Subject'])[0]

# Group by 'Split' and 'SubjectId' and sum numeric columns
agg = df_all.groupby(['Split', 'SubjectId'], as_index=False).agg({
    'Subject': 'max',  # Subject is now integer, max or min is fine since factorize is consistent
    'PA': 'sum',
    'AB': 'sum',
    'H': 'sum',
    'TB': 'sum',
    'BB': 'sum',
    'SF': 'sum',
    'HBP': 'sum'
})

# Reorder columns to match target schema
agg = agg[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

# Ensure correct dtypes
agg['SubjectId'] = agg['SubjectId'].astype(int)
agg['Subject'] = agg['Subject'].astype(int)
agg['PA'] = agg['PA'].astype(int)
agg['AB'] = agg['AB'].astype(int)
agg['H'] = agg['H'].astype(int)
agg['TB'] = agg['TB'].astype(int)
agg['BB'] = agg['BB'].astype(int)
agg['SF'] = agg['SF'].astype(int)
agg['HBP'] = agg['HBP'].astype(int)

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)