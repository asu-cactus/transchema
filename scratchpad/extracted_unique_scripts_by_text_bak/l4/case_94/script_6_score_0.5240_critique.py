import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

# Map Subject string to integer codes to match target schema
subject_map = {
    'HitterId': 1,
    'PitcherId': 2,
    'PitcherTeamId': 3,
    'HitterTeamId': 4
}

for df in [df0, df1, df2, df3]:
    df['Subject'] = df['Subject'].map(subject_map)

# Join df0 and df1 on ['Split', 'SubjectId', 'Subject']
df01 = pd.merge(df0, df1, on=['Split', 'SubjectId', 'Subject'], how='outer', suffixes=('_0', '_1'))

# Join the result with df2
df012 = pd.merge(df01, df2, on=['Split', 'SubjectId', 'Subject'], how='outer')

# Join the result with df3
df0123 = pd.merge(df012, df3, on=['Split', 'SubjectId', 'Subject'], how='outer', suffixes=('', '_3'))

# For columns with suffixes, fill NaN with 0 and sum across all sources
def sum_columns(base_col):
    cols = [col for col in df0123.columns if col == base_col or col.startswith(base_col + '_')]
    return df0123[cols].fillna(0).sum(axis=1)

numeric_cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']

result = df0123[['Split', 'SubjectId', 'Subject']].copy()

for col in numeric_cols:
    result[col] = sum_columns(col).astype(int)

# Group by keys to ensure uniqueness and sum again (in case of duplicates)
result = result.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA':'sum', 'AB':'sum', 'H':'sum', 'TB':'sum', 'BB':'sum', 'SF':'sum', 'HBP':'sum'
})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)