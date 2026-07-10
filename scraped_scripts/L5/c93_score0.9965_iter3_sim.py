import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_4.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

df_all['Winner'] = df_all['Winner'].str.upper().map({'YES':1}).fillna(0).astype(int)

grouped = df_all.groupby('Category').agg(
    Year=('Year', 'count'),
    Nominee=('Nominee', 'count'),
    Movie=('Movie', 'count'),
    Winner=('Winner', 'sum')
).reset_index()

grouped['Year'] = grouped['Year'].astype(int)
grouped['Nominee'] = grouped['Nominee'].astype(int)
grouped['Movie'] = grouped['Movie'].astype(int)
grouped['Winner'] = grouped['Winner'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_93/target_multisource_mcts.csv", index=False)