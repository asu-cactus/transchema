import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_90/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on=["Station", "Date"], suffixes=('', '_dup'))

id_vars = ['Station']
value_vars = [col for col in df0.columns if col not in ['Station', 'Date']]

df_unpivot = df0.melt(id_vars=id_vars, value_vars=value_vars, var_name='variable', value_name='value')

pivot_df = df_unpivot.pivot(index='Station', columns='variable', values='value').reset_index()

cols = ['Station', 'Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

for c in cols:
    if c != 'Station':
        pivot_df[c] = pd.to_numeric(pivot_df[c], errors='coerce').astype('Int64')

pivot_df = pivot_df[cols]

pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_90/target_multisource_mcts.csv", index=False)