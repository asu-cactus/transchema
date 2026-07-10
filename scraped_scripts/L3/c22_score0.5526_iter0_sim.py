import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)

grouped = df0.groupby(['Department', 'Term'], as_index=False)['Reg Count'].sum()

pivoted = grouped.pivot(index='Department', columns='Term', values='Reg Count').fillna(0)

pivoted.columns = pivoted.columns.astype(str)

result = pivoted.reset_index()

for col in ['20153', '20161', '20162']:
    if col not in result.columns:
        result[col] = 0.0

result = result[['Department', '20153', '20161', '20162']]

result[['20153', '20161', '20162']] = result[['20153', '20161', '20162']].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)