import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

# Group by 'id' (unique key), aggregate other columns by first
grouped = df0.groupby('id', as_index=False).agg({
    'neighbourhood': 'first',
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

# Convert string columns to categorical codes (integer)
# Columns in target schema that are integer but string in source: name, host_name, neighbourhood_group, room_type, last_review
# 'neighbourhood' remains string as in target

for col in ['name', 'host_name', 'neighbourhood_group', 'room_type', 'last_review']:
    grouped[col] = grouped[col].astype('category').cat.codes

# 'reviews_per_month' is float in source, integer in target - convert by rounding or truncation
grouped['reviews_per_month'] = pd.to_numeric(grouped['reviews_per_month'], errors='coerce').fillna(0).astype(int)

# Convert other numeric columns to int (some may be float)
int_cols = ['host_id', 'latitude', 'longitude', 'price', 'minimum_nights', 'number_of_reviews',
            'calculated_host_listings_count', 'availability_365']

for col in int_cols:
    grouped[col] = pd.to_numeric(grouped[col], errors='coerce').fillna(0).astype(int)

# 'id' is already int, ensure it
grouped['id'] = pd.to_numeric(grouped['id'], errors='coerce').fillna(0).astype(int)

# 'neighbourhood' remains string
grouped['neighbourhood'] = grouped['neighbourhood'].astype(str)

# Reorder columns to match target schema exactly
target_cols = ['neighbourhood', 'id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
               'latitude', 'longitude', 'room_type', 'price', 'minimum_nights', 'number_of_reviews',
               'last_review', 'reviews_per_month', 'calculated_host_listings_count', 'availability_365']

grouped = grouped[target_cols]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)