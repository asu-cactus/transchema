import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

# Define group by columns
group_by_cols = ['day_week', 'weekday']

# Define aggregation dictionary
agg_dict = {
    'ENTRIESn': 'sum',
    'EXITSn': 'sum',
    'ENTRIESn_hourly': 'sum',
    'EXITSn_hourly': 'sum',
    'hour': 'mean',
    'fog': 'sum',
    'precipi': 'sum',
    'pressurei': 'mean',
    'rain': 'sum',
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

# Cast columns to target types
df_agg['day_week'] = df_agg['day_week'].astype(int)
df_agg['weekday'] = df_agg['weekday'].astype(int)

# Ensure all other columns are float (they should be by default)
for col in df_agg.columns:
    if col not in group_by_cols:
        df_agg[col] = df_agg[col].astype(float)

# Reorder columns to match target schema exactly
target_columns = ['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday',
                  'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi',
                  'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']

# latitude and longitude are missing in group_by or agg_dict, add them as mean aggregations
# They were missing in agg_dict, add them now:
# So we need to add latitude and longitude mean aggregation as well

# Recompute with latitude and longitude included
agg_dict.update({'latitude': 'mean', 'longitude': 'mean'})

df_agg = df0.groupby(group_by_cols).agg(agg_dict).reset_index()

df_agg['day_week'] = df_agg['day_week'].astype(int)
df_agg['weekday'] = df_agg['weekday'].astype(int)

for col in df_agg.columns:
    if col not in group_by_cols:
        df_agg[col] = df_agg[col].astype(float)

df_agg = df_agg[target_columns]

# Save to CSV
df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)