import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_89/training_0.csv", index_col=0)

cols = ['Station', 'Tmax', 'Tmin', 'Tavg', 'Depart', 'DewPoint', 'WetBulb', 'Heat', 'Cool', 'Sunrise', 'Sunset', 'CodeSum', 'Depth', 'Water1', 'SnowFall', 'PrecipTotal', 'StnPressure', 'SeaLevel', 'ResultSpeed', 'ResultDir', 'AvgSpeed']

df = df[cols]

# Convert all columns to numeric, coercing errors and filling NaN with 0 for counting
df = df.apply(pd.to_numeric, errors='coerce')

# Group by Station and count non-null values in each column except Station
agg_dict = {col: 'count' for col in cols if col != 'Station'}

df_agg = df.groupby('Station').agg(agg_dict).reset_index()

# Convert all columns to int as target schema requires integer types
df_agg = df_agg.astype(int)

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_89/target_multisource_mcts.csv", index=False)