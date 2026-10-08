import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_90/training_0.csv", index_col=0)

# Convert all columns except 'Station' and 'Date' to numeric, coercing errors to NaN
cols_to_convert = [col for col in df0.columns if col not in ['Station', 'Date']]
df0[cols_to_convert] = df0[cols_to_convert].apply(pd.to_numeric, errors='coerce')

# Group by 'Station' and count non-null values for each column except 'Date' and 'Station'
agg_cols = ['Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool',
            'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal',
            'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

df_grouped = df0.groupby('Station')[agg_cols].count().reset_index()

# Ensure columns are in the target order
cols = ['Station'] + agg_cols
df_grouped = df_grouped[cols]

# Convert all columns except 'Station' to integer type (Int64 to allow NA if any)
for c in agg_cols:
    df_grouped[c] = df_grouped[c].astype('Int64')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_90/target_multisource_mcts.csv", index=False)