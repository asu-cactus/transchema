import pandas as pd
import numpy as np

# Read the single source table
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

# Convert last_review to datetime, then to integer timestamp (or 0 if NaT)
df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')
df['last_review'] = df['last_review'].map(lambda x: int(x.timestamp()) if pd.notnull(x) else 0)

# Define aggregation dictionary
agg_dict = {
    'id': 'count',  # count of rows per neighbourhood
    'name': 'count',
    'host_id': 'count',
    'host_name': 'count',
    'neighbourhood_group': 'count',
    'latitude': 'mean',
    'longitude': 'mean',
    'room_type': 'count',
    'price': 'mean',
    'minimum_nights': 'mean',
    'number_of_reviews': 'sum',
    'last_review': 'max',
    'reviews_per_month': 'mean',
    'calculated_host_listings_count': 'sum',
    'availability_365': 'sum'
}

# Group by neighbourhood and aggregate
df_agg = df.groupby('neighbourhood', as_index=False).agg(agg_dict)

# Round and convert all columns except 'neighbourhood' to int
for col in df_agg.columns:
    if col != 'neighbourhood':
        df_agg[col] = df_agg[col].round().astype(int)

# Reorder columns to match target schema exactly
cols = ['neighbourhood', 'id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
        'latitude', 'longitude', 'room_type', 'price', 'minimum_nights',
        'number_of_reviews', 'last_review', 'reviews_per_month',
        'calculated_host_listings_count', 'availability_365']

df_agg = df_agg[cols]

# Write output
df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)