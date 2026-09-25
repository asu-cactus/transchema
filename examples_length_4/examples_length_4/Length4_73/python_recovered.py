import pandas as pd

# Paths to source files
source0_path = 'autopipeline-benchmarks/github-pipelines/length4_73/test_0.csv'
source1_path = 'autopipeline-benchmarks/github-pipelines/length4_73/test_1.csv'

# Load sources with index_col=0 to ignore the first numeric column as per instructions
source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

# Aggregate source0 by city
agg_source0 = source0.groupby('city').agg(
    Average_Fare=('fare', 'mean'),
    Number_of_Rides=('ride_id', 'count')  # count rides per city
).reset_index()

# Rename columns to match target except those from source1
agg_source0.rename(columns={
    'city': 'City',
    'Average_Fare': 'Average Fare ($)',
    'Number_of_Rides': 'Number of Rides'
}, inplace=True)

# source1 has city, driver_count, type
# Rename columns to target schema
source1_renamed = source1.rename(columns={
    'city': 'City',
    'driver_count': 'Number of Drivers',
    'type': 'City Type'
})

# Merge aggregated source0 and source1 on 'City'
# Inner join is sufficient because target examples suggest only cities present in both sources
merged_df = pd.merge(agg_source0, source1_renamed, on='City', how='inner')

# Ensure correct data types as per target schema
merged_df['Average Fare ($)'] = merged_df['Average Fare ($)'].astype(float)
merged_df['Number of Rides'] = merged_df['Number of Rides'].astype(float)  # number of rides as float per target
merged_df['Number of Drivers'] = merged_df['Number of Drivers'].astype(int)
merged_df['City Type'] = merged_df['City Type'].astype(str)
merged_df['City'] = merged_df['City'].astype(str)

# Reorder columns exactly as target schema
merged_df = merged_df[['City', 'Average Fare ($)', 'Number of Rides', 'Number of Drivers', 'City Type']]

# Output path
output_path = 'autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_cot.csv'

# Save to CSV without index
merged_df.to_csv(output_path, index=False)