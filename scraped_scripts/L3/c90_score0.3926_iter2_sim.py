import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_90/training_0.csv", index_col=0)

cols = ['Station', 'Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

df = df[cols]

for c in cols:
    if c != 'Station':
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
df['Station'] = pd.to_numeric(df['Station'], errors='coerce').fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_90/target_multisource_mcts.csv", index=False)