import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_9/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_4.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

df_all['Year'] = df_all['Year'].str.extract(r'(\d+)').astype(int)
df_all['Category'] = df_all['Category'].astype('category').cat.codes + 1
df_all['Movie'] = df_all['Movie'].astype('category').cat.codes + 1
df_all['Winner'] = df_all['Winner'].map({'YES': 1, 'NO': 0}).fillna(0).astype(int)

df_all = df_all[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

df_grouped = df_all.groupby(['Nominee', 'Year', 'Category', 'Movie'], as_index=False).agg({'Winner': 'max'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)