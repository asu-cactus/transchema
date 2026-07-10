import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

df = df0.copy()

df['name'] = pd.to_numeric(df['name'], errors='coerce').fillna(df['id']).astype(int)
df['host_name'] = pd.to_numeric(df['host_name'], errors='coerce').fillna(df['host_id']).astype(int)
df['neighbourhood_group'] = pd.to_numeric(df['neighbourhood_group'], errors='coerce').fillna(0).astype(int)
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0).astype(int)
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0).astype(int)
df['room_type'] = pd.to_numeric(df['room_type'], errors='coerce').fillna(0).astype(int)
df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)
df['minimum_nights'] = pd.to_numeric(df['minimum_nights'], errors='coerce').fillna(0).astype(int)
df['number_of_reviews'] = pd.to_numeric(df['number_of_reviews'], errors='coerce').fillna(0).astype(int)
df['last_review'] = pd.to_numeric(pd.to_datetime(df['last_review'], errors='coerce').dt.strftime('%Y%m%d'), errors='coerce').fillna(0).astype(int)
df['reviews_per_month'] = pd.to_numeric(df['reviews_per_month'], errors='coerce').fillna(0).astype(int)
df['calculated_host_listings_count'] = pd.to_numeric(df['calculated_host_listings_count'], errors='coerce').fillna(0).astype(int)
df['availability_365'] = pd.to_numeric(df['availability_365'], errors='coerce').fillna(0).astype(int)

df_grouped = df.groupby('neighbourhood').agg({
    'id': 'max',
    'name': 'max',
    'host_id': 'max',
    'host_name': 'max',
    'neighbourhood_group': 'max',
    'latitude': 'max',
    'longitude': 'max',
    'room_type': 'max',
    'price': 'max',
    'minimum_nights': 'max',
    'number_of_reviews': 'max',
    'last_review': 'max',
    'reviews_per_month': 'max',
    'calculated_host_listings_count': 'max',
    'availability_365': 'max'
}).reset_index()

df_grouped = df_grouped.astype({
    'neighbourhood': str,
    'id': int,
    'name': int,
    'host_id': int,
    'host_name': int,
    'neighbourhood_group': int,
    'latitude': int,
    'longitude': int,
    'room_type': int,
    'price': int,
    'minimum_nights': int,
    'number_of_reviews': int,
    'last_review': int,
    'reviews_per_month': int,
    'calculated_host_listings_count': int,
    'availability_365': int
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)