import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_70/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Year'] = df['Year'].str.extract(r'(\d+)').astype(int)

df['Category'] = df['Category'].astype('category').cat.codes + 1

df['Nominee'] = df['Nominee'].astype(str)

df['Movie'] = df['Movie'].astype(str)

df['Winner'] = df['Winner'].map({'YES': 1}).fillna(0).astype(int)

df = df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

df = df.groupby(['Nominee', 'Year', 'Category', 'Movie'], as_index=False).agg({'Winner': 'max'})

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_70/target_multisource_mcts.csv", index=False)