import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

# Group by 'neighbourhood' and 'id' to get unique rows matching target count
grouped = df0.groupby(['neighbourhood', 'id'], as_index=False).agg({
    'name': 'first',
    'host_id': 'first',
    'host_name': 'first',
    'neighbourhood_group': 'first',
    'latitude': 'first',
    'longitude': 'first',
    'room_type': 'first',
    'price': 'first',
    'minimum_nights': 'first',
    'number_of_reviews': 'first',
    'last_review': 'first',
    'reviews_per_month': 'first',
    'calculated_host_listings_count': 'first',
    'availability_365': 'first'
})

# Convert string columns to categorical codes to match target integer columns
# Columns to convert: 'name', 'host_name', 'last_review', 'neighbourhood_group', 'room_type'
# 'neighbourhood_group' and 'room_type' are strings but categorical, convert to codes
for col in ['name', 'host_name', 'last_review', 'neighbourhood_group', 'room_type']:
    grouped[col] = pd.Categorical(grouped[col]).codes

# Convert 'neighbourhood' to string (target schema)
grouped['neighbourhood'] = grouped['neighbourhood'].astype(str)

# Convert all other columns to int (target schema)
int_cols = ['id', 'name', 'host_id', 'host_name', 'neighbourhood_group', 'latitude', 'longitude',
            'room_type', 'price', 'minimum_nights', 'number_of_reviews', 'last_review',
            'reviews_per_month', 'calculated_host_listings_count', 'availability_365']

for col in int_cols:
    grouped[col] = pd.to_numeric(grouped[col], errors='coerce').fillna(0).astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)