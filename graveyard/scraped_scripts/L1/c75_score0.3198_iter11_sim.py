import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

agg_df = df0.groupby(['neighbourhood', 'id'], dropna=False).agg({
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

# Convert columns to target types
agg_df['neighbourhood'] = agg_df['neighbourhood'].astype(str)
agg_df['id'] = pd.to_numeric(agg_df['id'], errors='coerce').fillna(0).astype(int)

for col in ['name', 'host_id', 'host_name', 'neighbourhood_group', 'latitude', 'longitude', 'room_type', 'price',
            'minimum_nights', 'number_of_reviews', 'reviews_per_month', 'calculated_host_listings_count', 'availability_365']:
    if col == 'last_review':
        # last_review is a date string, keep as string, fill NaN with empty string
        agg_df[col] = agg_df[col].fillna('').astype(str)
    else:
        # Convert to numeric, fill NaN with 0, then to int
        agg_df[col] = pd.to_numeric(agg_df[col], errors='coerce').fillna(0).astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)