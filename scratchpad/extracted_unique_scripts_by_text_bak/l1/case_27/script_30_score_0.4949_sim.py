import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

grouped = df0.groupby(['day_week', 'weekday', 'hour', 'latitude', 'longitude'], as_index=False).agg({
    'ENTRIESn': 'mean',
    'EXITSn': 'mean',
    'ENTRIESn_hourly': 'mean',
    'EXITSn_hourly': 'mean',
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
})

grouped['day_week'] = grouped['day_week'].astype(int)
grouped['weekday'] = grouped['weekday'].astype(int)
grouped['hour'] = grouped['hour'].astype(float)
grouped['latitude'] = grouped['latitude'].astype(float)
grouped['longitude'] = grouped['longitude'].astype(float)

grouped = grouped[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday', 'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)