import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_68/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_68/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_68/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_68/training_3.csv"
]

dfs = []
for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    year = 2013 + i
    df = df.copy()
    df['year'] = year
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

df_pivot = df_all.pivot(index='Wrestler', columns='year', values=['Wins', 'Losses', 'Draws'])

df_pivot.columns = [f"{year} {stat}" for stat, year in df_pivot.columns]

df_pivot = df_pivot.reset_index()

int_cols = df_pivot.columns.drop('Wrestler')
df_pivot[int_cols] = df_pivot[int_cols].fillna(0).astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_68/target_multisource_mcts.csv", index=False)