import pandas as pd

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

df_grouped = df0.groupby(group_by_cols).agg(agg_dict).reset_index()

# Reorder columns to match target schema exactly
target_cols = ['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday',
               'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi',
               'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']

# Note: 'weekday' is in group_by_cols but appears after 'hour' in target schema, so reorder accordingly
# The groupby columns are day_week and weekday, but target schema order is day_week, ENTRIESn, ..., hour, weekday, ...
# So we need to reorder columns accordingly.

# The current df_grouped columns are: day_week, weekday, ENTRIESn, EXITSn, ..., hour, ...
# We need to reorder to target_cols order.

# Create a mapping for columns in df_grouped to target_cols order
# day_week and weekday are groupby columns, so they exist
# The rest are aggregated columns

# Reorder columns:
df_out = df_grouped[['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday',
                     'latitude', 'longitude', 'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi',
                     'meanprecipi', 'meanpressurei', 'meantempi', 'meanwspdi', 'weather_lat', 'weather_lon']]

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)