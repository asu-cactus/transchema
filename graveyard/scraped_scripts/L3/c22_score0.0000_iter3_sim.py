import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_1.csv", index_col=0)

pivot = df0.pivot_table(index='Department', columns='Term', values='Reg Count', aggfunc='sum')

pivot = pivot.rename(columns={20153: '20153', 20161: '20161', 20162: '20162'})

result = pivot[['20153', '20161', '20162']].copy()
result.index.name = 'Department'
result.reset_index(inplace=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)