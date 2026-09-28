import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

df = df0.copy()

df = df.astype({
    'day_week': 'int64',
    'ENTRIESn': 'float64',
    'EXITSn': 'float64',
    'ENTRIESn_hourly': 'float64',
    'EXITSn_hourly': 'float64',
    'hour': 'int64',
    'weekday': 'float64',
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

# Group by day_week and hour, aggregate sums and means accordingly
agg_dict = {
    'ENTRIESn': 'sum',
    'EXITSn': 'sum',
    'ENTRIESn_hourly': 'sum',
    'EXITSn_hourly': 'sum',
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

df_grouped = df.groupby(['day_week', 'hour'], as_index=False).agg(agg_dict)

# Reorder columns to match target schema
df_grouped = df_grouped[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly',
                         'hour', 'weekday', 'latitude', 'longitude', 'fog', 'precipi', 'pressurei',
                         'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi',
                         'meanwspdi', 'weather_lat', 'weather_lon']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)