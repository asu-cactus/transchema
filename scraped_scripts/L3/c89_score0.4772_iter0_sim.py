import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_89/training_0.csv", index_col=0)

def to_numeric_with_na(series):
    return pd.to_numeric(series.replace(['M', '-', ''], np.nan), errors='coerce')

for col in ['Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']:
    df0[col] = to_numeric_with_na(df0[col])

grouped = df0.groupby('Station').agg({
    'Tmax': 'mean',
    'Tmin': 'mean',
    'Tavg': 'mean',
    'Depart': 'mean',
    'DewPoint': 'mean',
    'WetBulb': 'mean',
    'Heat': 'mean',
    'Cool': 'mean',
    'Sunrise': 'mean',
    'Sunset': 'mean',
    'CodeSum': 'mean',
    'Depth': 'mean',
    'Water1': 'mean',
    'SnowFall': 'mean',
    'PrecipTotal': 'mean',
    'StnPressure': 'mean',
    'SeaLevel': 'mean',
    'ResultSpeed': 'mean',
    'ResultDir': 'mean',
    'AvgSpeed': 'mean'
}).reset_index()

int_cols = ['Station', 'Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

for col in int_cols:
    grouped[col] = grouped[col].round().astype('Int64')

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_89/target_multisource_mcts.csv", index=False)