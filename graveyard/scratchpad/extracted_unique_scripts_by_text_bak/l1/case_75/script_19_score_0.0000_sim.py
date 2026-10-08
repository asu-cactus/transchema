import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

agg_funcs = {
    'id': 'min',
    'name': 'min',
    'host_id': 'min',
    'host_name': 'min',
    'neighbourhood_group': 'min',
    'latitude': 'min',
    'longitude': 'min',
    'room_type': 'min',
    'price': 'min',
    'minimum_nights': 'min',
    'number_of_reviews': 'min',
    'last_review': 'min',
    'reviews_per_month': 'min',
    'calculated_host_listings_count': 'min',
    'availability_365': 'min'
}

df0['name'] = pd.to_numeric(df0['name'], errors='coerce')
df0['host_name'] = pd.to_numeric(df0['host_name'], errors='coerce')
df0['neighbourhood_group'] = pd.to_numeric(df0['neighbourhood_group'], errors='coerce')
df0['room_type'] = pd.to_numeric(df0['room_type'], errors='coerce')
df0['last_review'] = pd.to_numeric(df0['last_review'], errors='coerce')
df0['reviews_per_month'] = pd.to_numeric(df0['reviews_per_month'], errors='coerce')

grouped = df0.groupby('neighbourhood', dropna=False).agg(agg_funcs).reset_index()

grouped = grouped.astype({
    'id': 'Int64',
    'name': 'Int64',
    'host_id': 'Int64',
    'host_name': 'Int64',
    'neighbourhood_group': 'Int64',
    'latitude': 'Int64',
    'longitude': 'Int64',
    'room_type': 'Int64',
    'price': 'Int64',
    'minimum_nights': 'Int64',
    'number_of_reviews': 'Int64',
    'last_review': 'Int64',
    'reviews_per_month': 'Int64',
    'calculated_host_listings_count': 'Int64',
    'availability_365': 'Int64'
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)