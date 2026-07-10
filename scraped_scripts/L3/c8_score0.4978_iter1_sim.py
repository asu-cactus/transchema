import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_3.csv", index_col=0)

df0['year'] = 2013
df1['year'] = 2014
df2['year'] = 2015
df3['year'] = 2016

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_pivot = df.pivot(index='Wrestler', columns='year', values=['Wins', 'Losses', 'Draws'])

df_pivot.columns = [f"{year} {stat}" for stat, year in df_pivot.columns]
df_pivot = df_pivot.reset_index()

for col in df_pivot.columns[1:]:
    df_pivot[col] = pd.to_numeric(df_pivot[col], errors='coerce').fillna(0).astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_8/target_multisource_mcts.csv", index=False)