import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

# Convert last_review to datetime to count non-null values
df0['last_review'] = pd.to_datetime(df0['last_review'], errors='coerce')

# Define aggregation functions
agg_dict = {
    'id': pd.Series.nunique,
    'name': pd.Series.nunique,
    'host_id': pd.Series.nunique,
    'host_name': pd.Series.nunique,
    'neighbourhood_group': pd.Series.nunique,
    'latitude': 'mean',
    'longitude': 'mean',
    'room_type': pd.Series.nunique,
    'price': 'mean',
    'minimum_nights': 'mean',
    'number_of_reviews': 'sum',
    'last_review': lambda x: x.notna().sum(),
    'reviews_per_month': 'mean',
    'calculated_host_listings_count': 'mean',
    'availability_365': 'mean'
}

grouped = df0.groupby('neighbourhood', dropna=False).agg(agg_dict).reset_index()

# Round and convert to integer as target schema expects integers
int_cols = ['id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
            'latitude', 'longitude', 'room_type', 'price', 'minimum_nights',
            'number_of_reviews', 'last_review', 'reviews_per_month',
            'calculated_host_listings_count', 'availability_365']

for col in int_cols:
    grouped[col] = grouped[col].round().astype('Int64')

# Reorder columns to match target schema exactly
target_cols = ['neighbourhood', 'id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
               'latitude', 'longitude', 'room_type', 'price', 'minimum_nights',
               'number_of_reviews', 'last_review', 'reviews_per_month',
               'calculated_host_listings_count', 'availability_365']

grouped = grouped[target_cols]

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)