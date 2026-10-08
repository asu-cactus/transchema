import pandas as pd
import numpy as np

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_90/training_0.csv", index_col=0)

cols = ['Station', 'Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

df = df[cols]

def to_int_or_nan(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float)):
        if pd.isna(x):
            return np.nan
        if isinstance(x, float) and x.is_integer():
            return int(x)
        if isinstance(x, int):
            return x
    try:
        if isinstance(x, str):
            x = x.strip()
            if x in ['M', '-', '']:
                return np.nan
            if x.isdigit() or (x.startswith('-') and x[1:].isdigit()):
                return int(x)
            f = float(x)
            if f.is_integer():
                return int(f)
            return int(round(f))
    except:
        return np.nan
    return np.nan

for c in cols:
    df[c] = df[c].apply(to_int_or_nan)

# Group by Station and count non-null values for all other columns
agg_dict = {c: 'count' for c in cols if c != 'Station'}

df_grouped = df.groupby('Station', as_index=False).agg(agg_dict)

# Convert counts to Int64 dtype (nullable integer)
for c in df_grouped.columns:
    if c != 'Station':
        df_grouped[c] = df_grouped[c].astype('Int64')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_90/target_multisource_mcts.csv", index=False)