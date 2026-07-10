import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_58/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)
df['Winner'] = df['Winner'].apply(lambda x: 1 if str(x).strip().upper() == 'YES' else 0)

df['Nominee'] = 1
df['Movie'] = 1

grouped = df.groupby('Category').agg({
    'Year': 'count',
    'Nominee': 'sum',
    'Movie': 'sum',
    'Winner': 'sum'
}).reset_index()

grouped = grouped.rename(columns={'Year': 'Year', 'Nominee': 'Nominee', 'Movie': 'Movie', 'Winner': 'Winner'})

grouped['Year'] = grouped['Year'].astype(int)
grouped['Nominee'] = grouped['Nominee'].astype(int)
grouped['Movie'] = grouped['Movie'].astype(int)
grouped['Winner'] = grouped['Winner'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_58/target_multisource_mcts.csv", index=False)