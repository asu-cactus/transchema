import pandas as pd
import numpy as np

def to_numeric_safe(series):
    return pd.to_numeric(series.replace(['M', '-', ''], np.nan), errors='coerce')

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_90/training_0.csv', index_col=0)

cols_to_clean = ['Depart', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'Sunrise', 'Sunset', 'SeaLevel', 'AvgSpeed']
for col in cols_to_clean:
    df0[col] = df0[col].replace(['M', '-', ''], np.nan)

numeric_cols = ['Station', 'Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

for col in numeric_cols:
    df0[col] = to_numeric_safe(df0[col])

group_by_cols = ['Depart', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'SeaLevel', 'AvgSpeed']

agg_dict = {
    'Station': 'mean',
    'Tmax': 'mean',
    'Tmin': 'mean',
    'Tavg': 'mean',
    'DewPoint': 'mean',
    'WetBulb': 'mean',
    'Heat': 'mean',
    'Cool': 'mean',
    'PrecipTotal': 'mean',
    'StnPressure': 'mean',
    'ResultSpeed': 'mean',
    'ResultDir': 'mean'
}

grouped = df0.groupby(group_by_cols, dropna=False).agg(agg_dict).reset_index()

# Round all columns to integers as target schema requires integer types
for col in grouped.columns:
    grouped[col] = grouped[col].round().astype('Int64')

# Reorder columns to match target schema
target_columns = ['Station', 'Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

# Some group_by columns are in index, so ensure all target columns exist
# 'Depart', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'SeaLevel', 'AvgSpeed' are group_by columns
# 'Water1' and 'AvgSpeed' are group_by columns but not aggregated, so they are present in grouped

# Ensure all columns exist in grouped, if not, add with NaN
for col in target_columns:
    if col not in grouped.columns:
        grouped[col] = pd.NA

grouped = grouped[target_columns]

grouped.to_csv('autopipeline-benchmarks/github-pipelines/length3_90/target_multisource_mcts.csv', index=False)