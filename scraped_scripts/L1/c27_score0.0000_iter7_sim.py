import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, left_on=['latitude', 'longitude'], right_on=['weather_lat', 'weather_lon'], suffixes=('', '_y'))

group_cols = ['day_week']
agg_dict = {
    'ENTRIESn': 'mean',
    'EXITSn': 'mean',
    'ENTRIESn_hourly': 'mean',
    'EXITSn_hourly': 'mean',
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
}

df_grouped = df_joined.groupby(group_cols).agg(agg_dict).reset_index()

df_grouped['day_week'] = df_grouped['day_week'].astype(int)
df_grouped['weekday'] = df_grouped['weekday'].round().astype(int)

df_grouped = df_grouped[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday', 'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)