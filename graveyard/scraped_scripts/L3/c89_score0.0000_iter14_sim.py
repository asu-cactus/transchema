import pandas as pd
import numpy as np

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_89/training_0.csv", index_col=0)

df_replace = df.replace({'M': np.nan, '-': np.nan, '': np.nan})

for col in df_replace.columns:
    if col != 'Station' and col != 'Date':
        df_replace[col] = pd.to_numeric(df_replace[col], errors='coerce')

pivoted = df_replace.pivot(index='Station', columns='Date')

agg_dict = {}
for col in df_replace.columns:
    if col not in ['Station', 'Date']:
        agg_dict[col] = 'max'

agg_df = pivoted.groupby(level=0).agg({col: 'max' for col in df_replace.columns if col not in ['Station', 'Date']})

agg_df.columns = agg_df.columns.droplevel(1)

agg_df = agg_df.reset_index()

target_cols = ['Station', 'Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

agg_df = agg_df[target_cols]

agg_df = agg_df.astype({col: 'Int64' for col in target_cols if col != 'Station'})

agg_df['Station'] = agg_df['Station'].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_89/target_multisource_mcts.csv", index=False)