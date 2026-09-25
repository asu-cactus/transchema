import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df = df.rename(columns={
    'neighbourhood': 'neighbourhood',
    'id': 'id',
    'name': 'name',
    'host_id': 'host_id',
    'host_name': 'host_name',
    'neighbourhood_group': 'neighbourhood_group',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'room_type': 'room_type',
    'price': 'price',
    'minimum_nights': 'minimum_nights',
    'number_of_reviews': 'number_of_reviews',
    'last_review': 'last_review',
    'reviews_per_month': 'reviews_per_month',
    'calculated_host_listings_count': 'calculated_host_listings_count',
    'availability_365': 'availability_365'
})

df['neighbourhood'] = df['neighbourhood'].astype(str)

int_cols = ['id', 'name', 'host_id', 'host_name', 'neighbourhood_group', 'latitude', 'longitude', 'room_type', 'price',
            'minimum_nights', 'number_of_reviews', 'reviews_per_month', 'calculated_host_listings_count', 'availability_365']

for col in int_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

df['last_review'] = pd.to_numeric(pd.to_datetime(df['last_review'], errors='coerce').dt.strftime('%Y%m%d'), errors='coerce').fillna(0).astype(int)

df = df[['neighbourhood', 'id', 'name', 'host_id', 'host_name', 'neighbourhood_group', 'latitude', 'longitude', 'room_type',
         'price', 'minimum_nights', 'number_of_reviews', 'last_review', 'reviews_per_month', 'calculated_host_listings_count',
         'availability_365']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)