import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_89/training_0.csv", index_col=0)

cols_group_by = ['Station', 'Depart', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'SeaLevel', 'AvgSpeed']
cols_agg = ['Tmax', 'Tmin', 'Tavg', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'PrecipTotal', 'StnPressure', 'ResultSpeed', 'ResultDir']

def to_numeric_safe(series):
    return pd.to_numeric(series.replace(['M', '-', ''], np.nan), errors='coerce')

for col in cols_group_by:
    df0[col] = to_numeric_safe(df0[col])

for col in cols_agg:
    df0[col] = to_numeric_safe(df0[col])

grouped = df0.groupby(cols_group_by, dropna=False)[cols_agg].mean().reset_index()

# Rename columns to target schema order and types
# Target schema: ['Station': int, 'Tmax': int, 'Tmin': int, 'Tavg': int, 'Depart': int, 'DewPoint': int, 'WetBulb': int, 'Heat': int, 'Cool': int, 'Sunrise': int, 'Sunset': int, 'CodeSum': int, 'Depth': int, 'Water1': int, 'SnowFall': int, 'PrecipTotal': int, 'StnPressure': int, 'SeaLevel': int, 'ResultSpeed': int, 'ResultDir': int, 'AvgSpeed': int]

# The group_by columns are mostly int, but some may have NaNs, so convert carefully
# For columns with NaN, convert to Int64 dtype (nullable integer)
int64_nullable_cols = ['Station', 'Depart', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'SeaLevel', 'AvgSpeed']

for col in int64_nullable_cols:
    grouped[col] = grouped[col].round().astype('Int64')

for col in cols_agg:
    grouped[col] = grouped[col].round().astype('Int64')

# Reorder columns to target schema
target_cols = ['Station', 'Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

result = grouped[target_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_89/target_multisource_mcts.csv", index=False)