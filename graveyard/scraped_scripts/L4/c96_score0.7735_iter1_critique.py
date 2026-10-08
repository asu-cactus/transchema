import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Convert 'Split' column: extract digits if possible, else convert to category codes
df['Split'] = df['Split'].str.extract(r'(\d+)')[0]
df['Split'] = pd.to_numeric(df['Split'], errors='coerce')
if df['Split'].isnull().any():
    # For rows where extraction failed, convert to category codes
    mask = df['Split'].isnull()
    df.loc[mask, 'Split'] = df.loc[mask, 'Split'].astype('category').cat.codes
df['Split'] = df['Split'].astype(int)

# Convert 'Subject' column to numeric if possible, else category codes
df['Subject'] = pd.to_numeric(df['Subject'], errors='coerce')
if df['Subject'].isnull().any():
    mask = df['Subject'].isnull()
    df.loc[mask, 'Subject'] = df.loc[mask, 'Subject'].astype('category').cat.codes
df['Subject'] = df['Subject'].astype(int)

# Ensure numeric columns are integers
for col in ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# Group by key columns and sum the numeric columns
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