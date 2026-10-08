import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_89/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_89/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

target_cols = ['Station', 'Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

df = df[target_cols]

def to_int_or_nan(x):
    try:
        if pd.isna(x):
            return np.nan
        if isinstance(x, str):
            x = x.strip()
            if x in ['M', '-', '']:
                return np.nan
            if x.isdigit() or (x.startswith('-') and x[1:].isdigit()):
                return int(x)
            # try float then int
            f = float(x)
            return int(round(f))
        if isinstance(x, (int, float)):
            if np.isnan(x):
                return np.nan
            return int(round(x))
        return np.nan
    except:
        return np.nan

for col in target_cols:
    df[col] = df[col].apply(to_int_or_nan)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_89/target_multisource_mcts.csv", index=False)