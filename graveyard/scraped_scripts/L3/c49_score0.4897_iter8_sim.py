import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_49/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_49/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df['min_rank'] = df['rank_on_list'].astype('Int64')
df['max_weeks_on_list'] = df['weeks_on_list'].astype('Int64')

result = df[['title', 'min_rank', 'max_weeks_on_list']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_49/target_multisource_mcts.csv", index=False)