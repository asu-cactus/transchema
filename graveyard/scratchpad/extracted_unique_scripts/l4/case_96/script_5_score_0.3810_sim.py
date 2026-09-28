import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['Split'] = df['Split'].astype(str).str.extract(r'(\d+)').astype(int, errors='ignore', copy=False).fillna(df['Split'])
df['Subject'] = pd.to_numeric(df['Subject'], errors='coerce').fillna(df['Subject'])
df['Subject'] = df['Subject'].astype(int, errors='ignore')

for col in ['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df = df[['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)