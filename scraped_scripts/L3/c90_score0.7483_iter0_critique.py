import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_90/training_0.csv", index_col=0)

def to_numeric_or_nan(series):
    return pd.to_numeric(series.replace(['M', '-', ''], np.nan), errors='coerce')

cols = ['Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 
        'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 
        'ResultSpeed', 'ResultDir', 'AvgSpeed']

for col in cols:
    df0[col] = to_numeric_or_nan(df0[col])

# Replace NaN with 0 before sum aggregation to avoid NaNs in sums
df0[cols] = df0[cols].fillna(0)

grouped = df0.groupby('Station').agg({col: 'sum' for col in cols}).reset_index()

# Convert all columns except 'Station' to integer type
for col in grouped.columns:
    if col != 'Station':
        grouped[col] = grouped[col].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_90/target_multisource_mcts.csv", index=False)