import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_49/training_0.csv", index_col=0)

df_unpivot = pd.melt(df, id_vars=['title'], value_vars=['rank_on_list', 'weeks_on_list'], var_name='metric', value_name='value')

agg = df_unpivot.groupby(['title', 'metric'], as_index=False)['value'].max()

min_rank = agg[agg['metric'] == 'rank_on_list'][['title', 'value']].rename(columns={'value': 'min_rank'})
max_weeks = agg[agg['metric'] == 'weeks_on_list'][['title', 'value']].rename(columns={'value': 'max_weeks_on_list'})

result = pd.merge(min_rank, max_weeks, on='title')

result['min_rank'] = result['min_rank'].astype(int)
result['max_weeks_on_list'] = result['max_weeks_on_list'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_49/target_multisource_mcts.csv", index=False)