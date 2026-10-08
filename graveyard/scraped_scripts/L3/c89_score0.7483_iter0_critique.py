import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_89/training_0.csv", index_col=0)

def to_numeric_with_na(series):
    return pd.to_numeric(series.replace(['M', '-', ''], np.nan), errors='coerce')

cols = ['Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 
        'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 
        'ResultSpeed', 'ResultDir', 'AvgSpeed']

for col in cols:
    df0[col] = to_numeric_with_na(df0[col])

# Fill NaN with 0 before summing
df0[cols] = df0[cols].fillna(0)

grouped = df0.groupby('Station').agg({col: 'sum' for col in cols}).reset_index()

# Convert all columns to integer type (Int64 to allow NA if any)
int_cols = ['Station'] + cols
for col in int_cols:
    grouped[col] = grouped[col].round().astype('Int64')

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_89/target_multisource_mcts.csv", index=False)