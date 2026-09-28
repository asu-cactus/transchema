import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

agg_df = df0.groupby(['day_week'], as_index=False).agg({
    'ENTRIESn': 'sum',
    'EXITSn': 'sum',
    'ENTRIESn_hourly': 'sum',
    'EXITSn_hourly': 'sum',
    'hour': 'mean',
    'weekday': 'mean',
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
})

agg_df['day_week'] = agg_df['day_week'].astype(int)
agg_df['weekday'] = agg_df['weekday'].round().astype(int)
agg_df['hour'] = agg_df['hour'].astype(float)

agg_df = agg_df[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday', 'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)