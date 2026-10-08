import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)

agg = df0.groupby(['Department', 'Term'], as_index=False)['Reg Count'].sum()

pivot = agg.pivot(index='Department', columns='Term', values='Reg Count')

pivot = pivot.rename(columns={20153: '20153', 20161: '20161', 20162: '20162'})

result = pivot.reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)