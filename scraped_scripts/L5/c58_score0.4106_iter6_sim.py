import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_58/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_58/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_58/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_58/training_4.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)
df['Nominee'] = df['Nominee'].astype(str)
df['Movie'] = df['Movie'].astype(str)
df['Winner'] = df['Winner'].map({'YES': 1}).fillna(0).astype(int)
df['Category'] = df['Category'].astype(str)

df = df[['Category', 'Year', 'Nominee', 'Movie', 'Winner']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_58/target_multisource_mcts.csv", index=False)