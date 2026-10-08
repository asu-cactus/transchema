import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

agg = df0.groupby(['day_week', 'weekday']).agg({
    'ENTRIESn': 'mean',
    'EXITSn': 'mean',
    'ENTRIESn_hourly': 'mean',
    'EXITSn_hourly': 'mean',
    'hour': 'mean',
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
}).reset_index()

agg['day_week'] = agg['day_week'].astype(int)
agg['weekday'] = agg['weekday'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)