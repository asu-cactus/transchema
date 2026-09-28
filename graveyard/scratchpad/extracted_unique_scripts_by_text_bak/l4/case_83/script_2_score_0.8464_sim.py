import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

# Source1 already has columns city, driver_count, type - no unpivot needed since driver_count and type are separate columns, 
# but the plan says UNPIVOT on Source1 columns [driver_count, type].
# However, unpivoting driver_count and type together doesn't make sense because type is categorical and driver_count is numeric.
# The partial plan suggests unpivoting, but source1 schema is city, driver_count, type which matches target schema except average_fare.
# So the unpivot step is likely a misunderstanding. Instead, we need to join source1 with source0 aggregated by city and type.

# Aggregate source0 by city to get average fare per city
avg_fare = source0.groupby('city', as_index=False)['fare'].mean()

# Join source1 with avg_fare on city
merged = pd.merge(source1, avg_fare, on='city', how='inner')

# Rename columns to match target schema
merged = merged.rename(columns={'fare': 'average_fare'})

# Ensure correct dtypes
merged['driver_count'] = merged['driver_count'].astype(int)
merged['city'] = merged['city'].astype(str)
merged['type'] = merged['type'].astype(str)
merged['average_fare'] = merged['average_fare'].astype(float)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)