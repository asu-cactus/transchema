import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

group_cols = ['day_week', 'weekday', 'hour', 'latitude', 'longitude']
agg_cols = ['ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']

agg_dict = {col: 'mean' for col in agg_cols}

result = df0.groupby(group_cols, as_index=False).agg(agg_dict)

# Ensure correct dtypes as per target schema
result['day_week'] = result['day_week'].astype(int)
result['weekday'] = result['weekday'].astype(int)
result['hour'] = result['hour'].astype(float)
for col in agg_cols:
    if col not in ['fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly']:
        result[col] = result[col].astype(float)
# The above is safe since all aggregated columns are numeric and mean returns float

result = result[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday', 'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)