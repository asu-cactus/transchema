import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

# Select relevant columns matching target schema
cols = ['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday',
        'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi',
        'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']

df = df[cols]

# Cast types as per target schema
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

# Group by day_week, weekday, hour
agg_dict = {
    'ENTRIESn': 'sum',
    'EXITSn': 'sum',
    'ENTRIESn_hourly': 'sum',
    'EXITSn_hourly': 'sum',
    'latitude': 'mean',
    'longitude': 'mean',
    'fog': 'mean',
    'precipi': 'mean',
    'pressurei': 'mean',
    'rain': 'mean',
    'tempi': 'mean',
    'wspdi': 'mean',
    'meanprecipi': 'mean',
    'meanpressurei': 'mean',
    'meantempi': 'mean',
    'meanwspdi': 'mean',
    'weather_lat': 'mean',
    'weather_lon': 'mean'
}

df_agg = df.groupby(['day_week', 'weekday', 'hour'], as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
target_cols = ['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday',
               'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi',
               'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']

df_agg = df_agg[target_cols]

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)