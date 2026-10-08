import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

agg_df = df0.groupby(['day_week', 'weekday'], as_index=False).agg({
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
})

agg_df = agg_df.astype({
    'day_week': 'int64',
    'weekday': 'int64',
    'ENTRIESn': 'float64',
    'EXITSn': 'float64',
    'ENTRIESn_hourly': 'float64',
    'EXITSn_hourly': 'float64',
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

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)