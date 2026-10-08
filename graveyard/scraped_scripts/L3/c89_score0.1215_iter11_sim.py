import pandas as pd
import numpy as np

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_89/training_0.csv", index_col=0)

def to_int_or_nan(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float)):
        return int(x)
    if isinstance(x, str):
        x = x.strip()
        if x in ['M', '-', '']:
            return np.nan
        try:
            f = float(x)
            return int(round(f))
        except:
            return np.nan
    return np.nan

cols = ['Station', 'Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

df = df[cols]

for c in cols:
    df[c] = df[c].apply(to_int_or_nan)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_89/target_multisource_mcts.csv", index=False)