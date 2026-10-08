import pandas as pd

# Paths to source CSV files
source0_path = 'autopipeline-benchmarks/github-pipelines/length4_72/test_0.csv'
source1_path = 'autopipeline-benchmarks/github-pipelines/length4_72/test_1.csv'

# Load source tables with index_col=0 to ignore the first index column in CSV
source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

# Aggregate Source 0:
# Calculate average fare (a) and number of rides (b) per city
source0_agg = source0.groupby('city').agg(
    a=('fare', 'mean'),
    b=('ride_id', 'count')
).reset_index()

# Join aggregated source0 with source1 on city using inner join to only keep cities present in both
joined = pd.merge(source0_agg, source1[['city']], on='city', how='inner')

# Select final columns for the target table
target_df = joined[['city', 'a', 'b']]

# Ensure correct types according to target schema: city str, a float, b int
target_df['city'] = target_df['city'].astype(str)
target_df['a'] = target_df['a'].astype(float)
target_df['b'] = target_df['b'].astype(int)

# Write to target CSV file
target_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_cot.csv', index=False)