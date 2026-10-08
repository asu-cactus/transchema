import pandas as pd

# Read source table
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

# Group by 'neighbourhood' and aggregate counts for all other columns
agg_dict = {
    'id': 'count',
    'name': 'count',
    'host_id': 'count',
    'host_name': 'count',
    'neighbourhood_group': 'count',
    'latitude': 'count',
    'longitude': 'count',
    'room_type': 'count',
    'price': 'count',
    'minimum_nights': 'count',
    'number_of_reviews': 'count',
    'last_review': 'count',
    'reviews_per_month': 'count',
    'calculated_host_listings_count': 'count',
    'availability_365': 'count'
}

result = df.groupby('neighbourhood', dropna=False).agg(agg_dict).reset_index()

# Ensure column order matches target schema
result = result[['neighbourhood', 'id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
                 'latitude', 'longitude', 'room_type', 'price', 'minimum_nights',
                 'number_of_reviews', 'last_review', 'reviews_per_month',
                 'calculated_host_listings_count', 'availability_365']]

# Cast all columns except 'neighbourhood' to int64 to match target schema
for col in result.columns:
    if col != 'neighbourhood':
        result[col] = result[col].astype('int64')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)