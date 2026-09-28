import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

# Group by day_week and weekday (both integers, leftmost columns)
grouped = df0.groupby(['day_week', 'weekday'], as_index=False).agg({
    'ENTRIESn': 'sum',
    'EXITSn': 'sum',
    'ENTRIESn_hourly': 'sum',
    'EXITSn_hourly': 'sum',
    'hour': 'sum',
    'fog': 'sum',
    'precipi': 'sum',
    'pressurei': 'sum',
    'rain': 'sum',
    'tempi': 'sum',
    'wspdi': 'sum',
    'meanprecipi': 'sum',
    'meanpressurei': 'sum',
    'meantempi': 'sum',
    'meanwspdi': 'sum',
    'weather_lat': 'sum',
    'weather_lon': 'sum'
})

# Cast types to match target schema
grouped['day_week'] = grouped['day_week'].astype(int)
grouped['weekday'] = grouped['weekday'].astype(int)

# Reorder columns to match target schema exactly
grouped = grouped[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly',
                   'hour', 'weekday', 'latitude', 'longitude', 'fog', 'precipi', 'pressurei',
                   'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi',
                   'meanwspdi', 'weather_lat', 'weather_lon']]

# The source does not have latitude and longitude in groupby or aggregation, so add them as mean per group
# Because latitude and longitude are missing in aggregation above, add them now:
# We must add latitude and longitude columns by mean aggregation per group

lat_long = df0.groupby(['day_week', 'weekday'], as_index=False).agg({
    'latitude': 'mean',
    'longitude': 'mean'
})

# Merge latitude and longitude back
grouped = pd.merge(grouped.drop(columns=['latitude', 'longitude'], errors='ignore'),
                   lat_long, on=['day_week', 'weekday'], how='left')

# Reorder columns again to match target schema
grouped = grouped[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly',
                   'hour', 'weekday', 'latitude', 'longitude', 'fog', 'precipi', 'pressurei',
                   'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi',
                   'meanwspdi', 'weather_lat', 'weather_lon']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)