import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Extract numeric values from 'Split' and 'Subject' columns
df['Split'] = df['Split'].astype(str).str.extract(r'(\d+)').astype(float).fillna(0).astype(int)
df['Subject'] = df['Subject'].astype(str).str.extract(r'(\d+)').astype(float).fillna(0).astype(int)

# Convert numeric columns to int
for col in ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# Group by the composite key and sum the numeric columns
df = df.groupby(['SubjectId', 'Split', 'Subject'], as_index=False).agg({
    'PA': 'sum',
    'AB': 'sum',
    'H': 'sum',
    'TB': 'sum',
    'BB': 'sum',
    'SF': 'sum',
    'HBP': 'sum'
})

# Reorder columns to match target schema exactly
df = df[['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)