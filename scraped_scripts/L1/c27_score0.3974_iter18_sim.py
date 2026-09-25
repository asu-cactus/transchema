import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

group_cols = ['conds', 'UNIT', 'DATEn', 'TIMEn', 'datetime', 'station']
agg_dict = {
    'hour': ['min', 'max'],
    'day_week': ['min', 'max'],
    'weekday': ['min', 'max'],
    'ENTRIESn': 'mean',
    'EXITSn': 'mean',
    'ENTRIESn_hourly': 'mean',
    'EXITSn_hourly': 'mean',
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

# Perform groupby aggregation
grouped = df.groupby(group_cols).agg(agg_dict)

# Flatten MultiIndex columns
grouped.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in grouped.columns.values]

# For hour, day_week, weekday take the min values (or max, but min is chosen here)
# The target schema expects single values for these, so pick min or max consistently
# Here, pick min for hour, day_week, weekday
grouped = grouped.reset_index()
grouped['hour'] = grouped['hour_min']
grouped['day_week'] = grouped['day_week_min'].astype(int)
grouped['weekday'] = grouped['weekday_min'].astype(int)

# Select and rename columns to match target schema
result = pd.DataFrame()
result['day_week'] = grouped['day_week']
result['ENTRIESn'] = grouped['ENTRIESn_mean']
result['EXITSn'] = grouped['EXITSn_mean']
result['ENTRIESn_hourly'] = grouped['ENTRIESn_hourly_mean']
result['EXITSn_hourly'] = grouped['EXITSn_hourly_mean']
result['hour'] = grouped['hour']
result['weekday'] = grouped['weekday']
result['latitude'] = grouped['latitude_mean']
result['longitude'] = grouped['longitude_mean']
result['fog'] = grouped['fog_mean']
result['precipi'] = grouped['precipi_mean']
result['pressurei'] = grouped['pressurei_mean']
result['rain'] = grouped['rain_mean']
result['tempi'] = grouped['tempi_mean']
result['wspdi'] = grouped['wspdi_mean']
result['meanprecipi'] = grouped['meanprecipi_mean']
result['meanpressurei'] = grouped['meanpressurei_mean']
result['meantempi'] = grouped['meantempi_mean']
result['meanwspdi'] = grouped['meanwspdi_mean']
result['weather_lat'] = grouped['weather_lat_mean']
result['weather_lon'] = grouped['weather_lon_mean']

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)