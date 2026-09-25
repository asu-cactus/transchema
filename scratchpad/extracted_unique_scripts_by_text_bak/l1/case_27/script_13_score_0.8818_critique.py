import pandas as pd

# Read the single source table (if multiple, read all and union)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

# If multiple source tables existed, we would union them here, e.g.:
# dfs = [df0, df1, df2, ...]
# df = pd.concat(dfs, ignore_index=True)
# Since only one source is given, just use df0 as df
df = df0

# Group by day_week and weekday (both integer, leftmost columns)
agg = df.groupby(['day_week', 'weekday']).agg(
    ENTRIESn=('ENTRIESn', 'sum'),
    EXITSn=('EXITSn', 'sum'),
    ENTRIESn_hourly=('ENTRIESn_hourly', 'sum'),
    EXITSn_hourly=('EXITSn_hourly', 'sum'),
    hour=('hour', 'mean'),
    latitude=('latitude', 'mean'),
    longitude=('longitude', 'mean'),
    fog=('fog', 'mean'),
    precipi=('precipi', 'mean'),
    pressurei=('pressurei', 'mean'),
    rain=('rain', 'mean'),
    tempi=('tempi', 'mean'),
    wspdi=('wspdi', 'mean'),
    meanprecipi=('meanprecipi', 'mean'),
    meanpressurei=('meanpressurei', 'mean'),
    meantempi=('meantempi', 'mean'),
    meanwspdi=('meanwspdi', 'mean'),
    weather_lat=('weather_lat', 'mean'),
    weather_lon=('weather_lon', 'mean')
).reset_index()

# Reorder columns exactly as target schema
agg = agg[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday',
           'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi',
           'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)