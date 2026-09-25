import pandas as pd

# File paths for sources
source_0_path = 'autopipeline-benchmarks/github-pipelines/length4_83/test_0.csv'
source_1_path = 'autopipeline-benchmarks/github-pipelines/length4_83/test_1.csv'
output_path = 'autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_cot.csv'

# Load sources with index_col=0 to ignore numeric index columns
df_source_0 = pd.read_csv(source_0_path, index_col=0)
df_source_1 = pd.read_csv(source_1_path, index_col=0)

# Aggregate Source 0 to get average fare by city
# Check data types, convert fare to float if needed
df_source_0['fare'] = df_source_0['fare'].astype(float)
avg_fare_by_city = df_source_0.groupby('city', as_index=False)['fare'].mean()
avg_fare_by_city.rename(columns={'fare': 'average_fare'}, inplace=True)

# Source 1 provides city, driver_count, and type - driver_count is integer, type is string
df_source_1['driver_count'] = df_source_1['driver_count'].astype(int)
df_source_1['type'] = df_source_1['type'].astype(str)

# Join Source 1 with the aggregated average fare from Source 0 on 'city'
df_merged = pd.merge(df_source_1, avg_fare_by_city, on='city', how='inner')

# Ensure final dataframe has correct column order and types consistent with target
df_merged = df_merged[['city', 'driver_count', 'type', 'average_fare']]

# Convert data types as per target schema
df_merged['city'] = df_merged['city'].astype(str)
df_merged['driver_count'] = df_merged['driver_count'].astype(int)
df_merged['type'] = df_merged['type'].astype(str)
df_merged['average_fare'] = df_merged['average_fare'].astype(float)

# Write the final dataframe to the output CSV file without the index
df_merged.to_csv(output_path, index=False)