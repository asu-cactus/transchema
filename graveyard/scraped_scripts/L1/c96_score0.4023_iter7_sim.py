import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

df0_sub = df0[['Publisher']].copy()
df0_sub['Publisher'] = df0_sub['Publisher'].astype(str).str.strip()

df1_pivot = df1.copy()
df1_pivot['Publisher'] = 1
df1_pivot = df1_pivot[['Publisher']]

df = pd.concat([df0_sub, df1_pivot], ignore_index=True)

df['Publisher'] = df['Publisher'].replace({'DC Comics': '1', 'Marvel Comics': '1'}).fillna('0')
df['Publisher'] = pd.to_numeric(df['Publisher'], errors='coerce').fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)