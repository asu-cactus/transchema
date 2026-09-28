import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

df = df.astype({
    'id': 'int64',
    'name': 'int64',
    'host_id': 'int64',
    'host_name': 'int64',
    'neighbourhood_group': 'int64',
    'neighbourhood': 'string',
    'latitude': 'int64',
    'longitude': 'int64',
    'room_type': 'int64',
    'price': 'int64',
    'minimum_nights': 'int64',
    'number_of_reviews': 'int64',
    'last_review': 'int64',
    'reviews_per_month': 'int64',
    'calculated_host_listings_count': 'int64',
    'availability_365': 'int64'
}, errors='ignore')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)