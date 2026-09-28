import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

unpivot_rows = []
for col in ['driver_count', 'type']:
    if col == 'driver_count':
        df_tmp = source1[['city', 'driver_count']].copy()
        df_tmp['type'] = 'driver_count'
        df_tmp.rename(columns={'driver_count': 'driver_count'}, inplace=True)
    else:
        df_tmp = source1[['city', 'type']].copy()
        df_tmp['driver_count'] = None
        df_tmp.rename(columns={'type': 'type'}, inplace=True)
    unpivot_rows.append(df_tmp)
unpivot_result = pd.concat(unpivot_rows, ignore_index=True)

# The above unpivot is not correct because 'type' is string, 'driver_count' is int.
# The partial plan says unpivot Source1 on value_vars=[driver_count, type] with var_name=type and value_name=driver_count.
# But 'type' is string, 'driver_count' is int, so unpivoting these two columns into one value column 'driver_count' and a 'type' column is ambiguous.
# Actually, the partial plan is likely a hint to reshape Source1 so that 'driver_count' and 'type' become rows under 'type' and 'driver_count' columns.
# But 'type' is string, so unpivoting 'type' column into 'driver_count' column is not possible.
# So the partial plan is probably incorrect or misleading.
# Instead, we should keep Source1 as is.

# The target schema is ['city', 'driver_count', 'type', 'average_fare']
# Source1 has ['city', 'driver_count', 'type']
# Source0 has ['city', 'date', 'fare', 'ride_id']

# We need to join Source1 and Source0 on city, then group by city and type, sum driver_count, average fare.

# So let's join Source1 and Source0 on city.

merged = pd.merge(source1, source0[['city', 'fare']], on='city', how='inner')

result = merged.groupby(['city', 'type'], as_index=False).agg({'driver_count':'sum', 'fare':'mean'})

result.rename(columns={'fare':'average_fare'}, inplace=True)

result['driver_count'] = result['driver_count'].astype(int)
result['type'] = result['type'].astype(str)
result['city'] = result['city'].astype(str)
result['average_fare'] = result['average_fare'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)