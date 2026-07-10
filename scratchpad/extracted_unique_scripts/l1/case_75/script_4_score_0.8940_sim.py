import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="id", suffixes=('', '_y'))

grouped = joined.groupby('neighbourhood', as_index=False).agg({
    'id': 'first',
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

# Convert columns to target types
grouped['neighbourhood'] = grouped['neighbourhood'].astype(str)
int_cols = ['id', 'name', 'host_id', 'host_name', 'neighbourhood_group', 'latitude', 'longitude', 'room_type', 'price',
            'minimum_nights', 'number_of_reviews', 'last_review', 'reviews_per_month', 'calculated_host_listings_count',
            'availability_365']

for col in int_cols:
    grouped[col] = pd.to_numeric(grouped[col], errors='coerce').fillna(0).astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)