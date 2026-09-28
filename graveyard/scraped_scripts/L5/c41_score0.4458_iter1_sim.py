import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_41/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_41/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_41/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_41/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_41/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)
df['Category'] = df['Category'].astype('category').cat.codes.astype(int)
df['Nominee'] = df['Nominee'].astype('category').cat.codes.astype(int)
df['Movie'] = df['Movie'].astype('category').cat.codes.astype(int)
df['Winner'] = df['Winner'].astype(str)

df = df[['Winner', 'Year', 'Category', 'Nominee', 'Movie']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_41/target_multisource_mcts.csv", index=False)