import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

df = df0.copy()

df = df.astype({
    'day_week': 'int64',
    'ENTRIESn': 'float64',
    'EXITSn': 'float64',
    'ENTRIESn_hourly': 'float64',
    'EXITSn_hourly': 'float64',
    'hour': 'float64',
    'weekday': 'int64',
    'latitude': 'float64',
    'longitude': 'float64',
    'fog': 'float64',
    'precipi': 'float64',
    'pressurei': 'float64',
    'rain': 'float64',
    'tempi': 'float64',
    'wspdi': 'float64',
    'meanprecipi': 'float64',
    'meanpressurei': 'float64',
    'meantempi': 'float64',
    'meanwspdi': 'float64',
    'weather_lat': 'float64',
    'weather_lon': 'float64'
})

df = df[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday', 'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)