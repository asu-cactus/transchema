import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df = df[df['Subject'].apply(lambda x: str(x).isdigit())]

df['Subject'] = df['Subject'].astype(int)
df['SubjectId'] = df['SubjectId'].astype(int)
df['PA'] = df['PA'].astype(int)
df['AB'] = df['AB'].astype(int)
df['H'] = df['H'].astype(int)
df['TB'] = df['TB'].astype(int)
df['BB'] = df['BB'].astype(int)
df['SF'] = df['SF'].astype(int)
df['HBP'] = df['HBP'].astype(int)

df = df[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)