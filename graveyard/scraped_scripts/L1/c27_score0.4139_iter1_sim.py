import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

# The partial plan suggests a self-join on day_week, weekday, hour, latitude, longitude.
# But joining the same table on identical keys will produce duplicates and no new info.
# Since only one source table is given, and the target schema columns are all present in df0,
# we can just select and cast columns to match the target schema.

# Select and cast columns to target schema types
df = df0[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday', 'latitude', 'longitude',
          'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi',
          'meanwspdi', 'weather_lat', 'weather_lon']].copy()

df['day_week'] = df['day_week'].astype(int)
df['weekday'] = df['weekday'].astype(int)
df['ENTRIESn'] = df['ENTRIESn'].astype(float)
df['EXITSn'] = df['EXITSn'].astype(float)
df['ENTRIESn_hourly'] = df['ENTRIESn_hourly'].astype(float)
df['EXITSn_hourly'] = df['EXITSn_hourly'].astype(float)
df['hour'] = df['hour'].astype(float)
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)
df['fog'] = df['fog'].astype(float)
df['precipi'] = df['precipi'].astype(float)
df['pressurei'] = df['pressurei'].astype(float)
df['rain'] = df['rain'].astype(float)
df['tempi'] = df['tempi'].astype(float)
df['wspdi'] = df['wspdi'].astype(float)
df['meanprecipi'] = df['meanprecipi'].astype(float)
df['meanpressurei'] = df['meanpressurei'].astype(float)
df['meantempi'] = df['meantempi'].astype(float)
df['meanwspdi'] = df['meanwspdi'].astype(float)
df['weather_lat'] = df['weather_lat'].astype(float)
df['weather_lon'] = df['weather_lon'].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv")