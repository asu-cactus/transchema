import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="user_id", suffixes=('_left', '_right'))

df_unpivot = pd.melt(df_joined, id_vars=['user_id', 'time_left', 'time_right'], value_vars=['bet_left', 'win_left', 'bet_right', 'win_right'], var_name='variable', value_name='value')

def extract_time(row):
    if 'left' in row['variable']:
        return row['time_left']
    else:
        return row['time_right']

df_unpivot['time'] = df_unpivot.apply(extract_time, axis=1)

df_unpivot['variable'] = df_unpivot['variable'].str.replace('_left', '').str.replace('_right', '')

df_pivot = df_unpivot.pivot_table(index=['user_id', 'time'], columns='variable', values='value', aggfunc='first').reset_index()

df_pivot = df_pivot[['user_id', 'time', 'bet', 'win']]

df_pivot['user_id'] = df_pivot['user_id'].astype(str)
df_pivot['time'] = df_pivot['time'].astype(str)
df_pivot['bet'] = pd.to_numeric(df_pivot['bet'], errors='coerce')
df_pivot['win'] = pd.to_numeric(df_pivot['win'], errors='coerce')

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)