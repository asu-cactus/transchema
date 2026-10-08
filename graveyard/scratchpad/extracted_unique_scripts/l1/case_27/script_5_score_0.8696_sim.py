import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

agg = df0.groupby('day_week').agg(
    ENTRIESn=('ENTRIESn', 'sum'),
    EXITSn=('EXITSn', 'sum'),
    ENTRIESn_hourly=('ENTRIESn_hourly', 'sum'),
    EXITSn_hourly=('EXITSn_hourly', 'sum'),
    hour_min=('hour', 'min'),
    hour_max=('hour', 'max'),
    weekday=('weekday', 'mean'),
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

# For 'hour' column in target schema, use the mean of min and max hour as a float
agg['hour'] = (agg['hour_min'] + agg['hour_max']) / 2
agg = agg.drop(columns=['hour_min', 'hour_max'])

agg = agg[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday', 'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)