import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_2.csv", index_col=0)

pivot = source2.pivot(index='Country Name', columns='Indicator Name', values='2015').reset_index()

join0 = pd.merge(pivot, source0, left_on='Country Name', right_on='Country', how='inner')

join1 = pd.merge(join0, source1, on='Country', how='inner')

grouped = join1.groupby('Rank', as_index=False).agg({'GDP at market prices (constant 2010 US$)': 'sum'})

grouped.rename(columns={'GDP at market prices (constant 2010 US$)': '0'}, inplace=True)

grouped['Rank'] = grouped['Rank'].astype(int)
grouped['0'] = grouped['0'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_100/target_multisource_mcts.csv", index=False)