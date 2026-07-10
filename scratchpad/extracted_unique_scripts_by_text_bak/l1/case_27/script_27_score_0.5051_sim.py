import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_27/training_0.csv", index_col=0)

# The partial plan suggests a self-join on day_week and hour, but joining the same table on identical keys yields the same table.
# So effectively, this is a no-op for this single source.
# We proceed with the data as is.

# The target schema columns:
target_cols = ['day_week', 'ENTRIESn', 'EXITSn', 'ENTRIESn_hourly', 'EXITSn_hourly', 'hour', 'weekday', 'latitude', 'longitude',
               'fog', 'precipi', 'pressurei', 'rain', 'tempi', 'wspdi', 'meanprecipi', 'meanpressurei', 'meantempi',
               'meanwspdi', 'weather_lat', 'weather_lon']

# The source df0 already contains all these columns except 'day_week' is integer, 'hour' is float in target (hour is int in source),
# so convert hour to float.
df0['hour'] = df0['hour'].astype(float)
df0['day_week'] = df0['day_week'].astype(int)
df0['weekday'] = df0['weekday'].astype(int)

# The partial plan includes UNPIVOT, but the target schema has separate columns for ENTRIESn, EXITSn, ENTRIESn_hourly, EXITSn_hourly,
# so no unpivoting is needed here. The source already has these columns.

# Select and reorder columns to match target schema exactly
df_target = df0[target_cols]

# Save to the target CSV
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_27/target_multisource_mcts.csv", index=False)