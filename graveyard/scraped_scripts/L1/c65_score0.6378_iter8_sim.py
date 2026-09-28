import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)

pivoted = df0.groupby(['year', 'runtime']).size().reset_index(name='count')
pivoted2 = pivoted.pivot(index='year', columns='runtime', values='count').fillna(0).astype(int)
pivoted2 = pivoted2.reset_index()

if '0' not in pivoted2.columns:
    pivoted2['0'] = 0
pivoted2 = pivoted2[['year', 0]] if 0 in pivoted2.columns else pivoted2[['year', '0']]

pivoted2.columns = ['year', '0']

pivoted2.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)