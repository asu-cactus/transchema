import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_49/training_0.csv", index_col=0)
df0['title'] = df0['title'].str.upper()
df = df0[['title', 'rank_on_list', 'weeks_on_list']].copy()
df.rename(columns={'rank_on_list': 'min_rank', 'weeks_on_list': 'max_weeks_on_list'}, inplace=True)
df['min_rank'] = df['min_rank'].astype(int)
df['max_weeks_on_list'] = df['max_weeks_on_list'].astype(int)
df.to_csv("autopipeline-benchmarks/github-pipelines/length3_49/target_multisource_mcts.csv", index=False)