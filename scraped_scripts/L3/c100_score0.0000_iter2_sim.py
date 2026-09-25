import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_2.csv", index_col=0)

pivot_df2 = df2.pivot(index='Country Name', columns='Indicator Name', values='2015').reset_index()

join1 = pd.merge(pivot_df2, df0, left_on='Country Name', right_on='Country', how='inner')
join2 = pd.merge(join1, df1, left_on='Country', right_on='Country', how='inner')

result = join2[['Rank', 'GDP at market prices (constant 2010 US$)']].copy()
result.rename(columns={'GDP at market prices (constant 2010 US$)': '0'}, inplace=True)
result['Rank'] = result['Rank'].astype(int)
result['0'] = result['0'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_100/target_multisource_mcts.csv", index=False)