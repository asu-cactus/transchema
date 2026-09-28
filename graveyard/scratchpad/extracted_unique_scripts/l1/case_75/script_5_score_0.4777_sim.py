import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

agg = df.groupby(['neighbourhood', 'id'], as_index=False).agg(
    host_id=('host_id', 'count'),
    price=('price', 'mean'),
    availability_365=('availability_365', 'max')
)

agg = agg.rename(columns={
    'host_id': 'host_id',
    'price': 'price',
    'availability_365': 'availability_365'
})

# The target schema requires many columns that are not aggregated in the partial plan.
# Since the partial plan only aggregates host_id count, price avg, availability max,
# but target schema has many columns, we must fill missing columns.

# The target schema columns:
# ['neighbourhood': string, 'id': integer, 'name': integer, 'host_id': integer, 'host_name': integer,
#  'neighbourhood_group': integer, 'latitude': integer, 'longitude': integer, 'room_type': integer,
#  'price': integer, 'minimum_nights': integer, 'number_of_reviews': integer, 'last_review': integer,
#  'reviews_per_month': integer, 'calculated_host_listings_count': integer, 'availability_365': integer]

# The aggregation only provides neighbourhood, id, host_id (count), price (avg), availability_365 (max).
# The other columns are missing.

# To fill the other columns, we can take the first value per group from the original df for those columns.

firsts = df.groupby(['neighbourhood', 'id'], as_index=False).first()

# Merge aggregated columns with firsts for other columns
result = pd.merge(firsts, agg[['neighbourhood', 'id', 'host_id', 'price', 'availability_365']],
                  on=['neighbourhood', 'id'], suffixes=('_first', ''))

# Replace columns with aggregated values where applicable
result['host_id'] = result['host_id']
result['price'] = result['price']
result['availability_365'] = result['availability_365']

# Select and reorder columns to match target schema
cols = ['neighbourhood', 'id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
        'latitude', 'longitude', 'room_type', 'price', 'minimum_nights', 'number_of_reviews',
        'last_review', 'reviews_per_month', 'calculated_host_listings_count', 'availability_365']

result = result[cols]

# Convert columns to appropriate types
result['id'] = result['id'].astype(int)
result['name'] = pd.to_numeric(result['name'], errors='coerce').fillna(0).astype(int)
result['host_id'] = result['host_id'].astype(int)
result['host_name'] = pd.to_numeric(result['host_name'], errors='coerce').fillna(0).astype(int)
result['neighbourhood_group'] = pd.to_numeric(result['neighbourhood_group'], errors='coerce').fillna(0).astype(int)
result['latitude'] = pd.to_numeric(result['latitude'], errors='coerce').fillna(0).astype(int)
result['longitude'] = pd.to_numeric(result['longitude'], errors='coerce').fillna(0).astype(int)
result['room_type'] = pd.to_numeric(result['room_type'], errors='coerce').fillna(0).astype(int)
result['price'] = result['price'].round().astype(int)
result['minimum_nights'] = pd.to_numeric(result['minimum_nights'], errors='coerce').fillna(0).astype(int)
result['number_of_reviews'] = pd.to_numeric(result['number_of_reviews'], errors='coerce').fillna(0).astype(int)
result['last_review'] = pd.to_numeric(result['last_review'], errors='coerce').fillna(0).astype(int)
result['reviews_per_month'] = pd.to_numeric(result['reviews_per_month'], errors='coerce').fillna(0).astype(int)
result['calculated_host_listings_count'] = pd.to_numeric(result['calculated_host_listings_count'], errors='coerce').fillna(0).astype(int)
result['availability_365'] = result['availability_365'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)