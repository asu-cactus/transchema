import pandas as pd

# Read source table
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

# Group by 'neighbourhood' only
agg = df.groupby('neighbourhood', as_index=False).agg(
    id_count=('id', 'count'),  # count of listings per neighbourhood
    price_avg=('price', 'mean'),
    availability_max=('availability_365', 'max'),
    minimum_nights_sum=('minimum_nights', 'sum'),
    number_of_reviews_sum=('number_of_reviews', 'sum'),
    last_review_max=('last_review', 'max'),
    reviews_per_month_avg=('reviews_per_month', 'mean'),
    calculated_host_listings_count_max=('calculated_host_listings_count', 'max')
)

# For string columns that appear in target schema, take first value per neighbourhood
firsts = df.groupby('neighbourhood', as_index=False).first()

# Merge aggregated numeric columns with first string columns
result = pd.merge(firsts[['neighbourhood', 'name', 'host_id', 'host_name', 'neighbourhood_group', 'latitude', 'longitude', 'room_type']],
                  agg,
                  on='neighbourhood',
                  how='inner')

# Create 'id' column as integer code for 'neighbourhood'
result['id'] = pd.factorize(result['neighbourhood'])[0] + 1  # start from 1 to match target examples

# Convert string columns to integer codes
for col in ['name', 'host_name', 'neighbourhood_group', 'room_type']:
    result[col] = pd.factorize(result[col])[0] + 1

# Convert 'last_review_max' (date string) to integer by factorizing unique dates
result['last_review'] = pd.factorize(result['last_review_max'])[0] + 1

# Rename columns to match target schema
result = result.rename(columns={
    'id_count': 'id',  # We already have 'id' as code, so keep 'id' as code, drop id_count
    'price_avg': 'price',
    'availability_max': 'availability_365',
    'minimum_nights_sum': 'minimum_nights',
    'number_of_reviews_sum': 'number_of_reviews',
    'reviews_per_month_avg': 'reviews_per_month',
    'calculated_host_listings_count_max': 'calculated_host_listings_count'
})

# Drop 'id_count' column because 'id' is the code column
result = result.drop(columns=['id_count', 'last_review_max'])

# Reorder columns to match target schema
cols = ['neighbourhood', 'id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
        'latitude', 'longitude', 'room_type', 'price', 'minimum_nights', 'number_of_reviews',
        'last_review', 'reviews_per_month', 'calculated_host_listings_count', 'availability_365']

result = result[cols]

# Convert all columns to int where appropriate
result['id'] = result['id'].astype(int)
result['name'] = result['name'].astype(int)
result['host_id'] = result['host_id'].astype(int)
result['host_name'] = result['host_name'].astype(int)
result['neighbourhood_group'] = result['neighbourhood_group'].astype(int)
result['latitude'] = result['latitude'].astype(int)
result['longitude'] = result['longitude'].astype(int)
result['room_type'] = result['room_type'].astype(int)
result['price'] = result['price'].round().astype(int)
result['minimum_nights'] = result['minimum_nights'].astype(int)
result['number_of_reviews'] = result['number_of_reviews'].astype(int)
result['last_review'] = result['last_review'].astype(int)
result['reviews_per_month'] = result['reviews_per_month'].round().astype(int)
result['calculated_host_listings_count'] = result['calculated_host_listings_count'].astype(int)
result['availability_365'] = result['availability_365'].astype(int)

# Save to target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)