import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Keep only rows where 'Subject' is numeric (convertible to int)
df = df[df['Subject'].apply(lambda x: str(x).isdigit())]

# Convert columns to correct types
df['Subject'] = df['Subject'].astype(int)
df['SubjectId'] = df['SubjectId'].astype(int)
df['PA'] = df['PA'].astype(int)
df['AB'] = df['AB'].astype(int)
df['H'] = df['H'].astype(int)
df['TB'] = df['TB'].astype(int)
df['BB'] = df['BB'].astype(int)
df['SF'] = df['SF'].astype(int)
df['HBP'] = df['HBP'].astype(int)

# Group by the leftmost columns of the target schema and sum the rest
df = df.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA': 'sum',
    'AB': 'sum',
    'H': 'sum',
    'TB': 'sum',
    'BB': 'sum',
    'SF': 'sum',
    'HBP': 'sum'
})

# Reorder columns to match target schema exactly
df = df[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)