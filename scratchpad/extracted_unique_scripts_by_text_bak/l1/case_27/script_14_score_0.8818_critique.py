import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

# Convert types to match target schema
df0['day_week'] = df0['day_week'].astype(int)
df0['weekday'] = df0['weekday'].astype(int)
df0['hour'] = df0['hour'].astype(float)

# Define group by columns
group_by_cols = ['day_week', 'weekday']

# Define aggregation mapping
agg_dict = {
    'ENTRIESn': 'sum',
    'EXITSn': 'sum',
    'ENTRIESn_hourly': 'sum',
    'EXITSn_hourly': 'sum',
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
}

# Perform group by and aggregation
df_agg = df0.groupby(group_by_cols).agg(agg_dict).reset_index()

# Reorder columns to match target schema exactly
target_cols = ['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday', 'latitude', 'longitude',
               'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi',
               'meanwspdi', 'weather_lat', 'weather_lon']

df_target = df_agg[target_cols]

# Save to target CSV
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)