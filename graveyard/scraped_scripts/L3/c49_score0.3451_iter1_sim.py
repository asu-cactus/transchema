import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_49/training_0.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_49/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)

df_joined = pd.merge(df0, df0, on="title", suffixes=('_left', '_right'))

result = pd.DataFrame()
result['title'] = df_joined['title']

result['min_rank'] = pd.to_numeric(df_joined[['rank_on_list_left', 'rank_on_list_right']].min(axis=1), errors='coerce').astype('Int64')
result['max_weeks_on_list'] = pd.to_numeric(df_joined[['weeks_on_list_left', 'weeks_on_list_right']].max(axis=1), errors='coerce').astype('Int64')

result.to_csv(target_path, index=False)