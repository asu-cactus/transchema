import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

numeric_cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df_grouped = df.groupby(['Split', 'SubjectId', 'Subject'], as_index=False)[numeric_cols].sum()

df_grouped['SubjectId'] = df_grouped['SubjectId'].astype('Int64')

df_grouped['Subject'] = pd.to_numeric(df_grouped['Subject'], errors='coerce').astype('Int64')

df_grouped = df_grouped[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)