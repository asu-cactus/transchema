import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_41/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_41/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_41/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_41/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_41/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_all['Year'] = df_all['Year'].str.extract(r'(\d{4})').astype(int)
df_all['Category'] = df_all['Category'].astype('category').cat.codes
df_all['Nominee'] = df_all['Nominee'].astype('category').cat.codes
df_all['Movie'] = df_all['Movie'].astype('category').cat.codes

grouped = df_all.groupby(['Winner', 'Category'], as_index=False).agg(Year=('Year', 'count'))

grouped = grouped.rename(columns={'Year': 'Year'})

grouped['Nominee'] = grouped['Year']
grouped['Movie'] = grouped['Year']

grouped = grouped[['Winner', 'Year', 'Category', 'Nominee', 'Movie']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_41/target_multisource_mcts.csv", index=False)