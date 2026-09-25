import pandas as pd

# Read source table
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

# Convert 'last_review' to datetime, keep NaT for missing
df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')

# Define aggregation dictionary
agg_dict = {
    'id': 'count',  # count of listings per neighbourhood
    'name': 'count',  # count of listings (same as id)
    'host_id': pd.Series.nunique,  # unique hosts
    'host_name': pd.Series.nunique,  # unique host names
    'neighbourhood_group': pd.Series.nunique,  # unique groups
    'latitude': 'mean',
    'longitude': 'mean',
    'room_type': pd.Series.nunique,
    'price': 'mean',
    'minimum_nights': 'mean',
    'number_of_reviews': 'sum',
    'last_review': 'max',  # latest review date
    'reviews_per_month': 'mean',
    'calculated_host_listings_count': 'mean',
    'availability_365': 'mean'
}

# Group by 'neighbourhood' and aggregate
grouped = df.groupby('neighbourhood').agg(agg_dict).reset_index()

# Convert 'last_review' datetime to integer ordinal (days since 0001-01-01)
# For NaT, fill with 0
grouped['last_review'] = grouped['last_review'].apply(lambda x: x.toordinal() if pd.notnull(x) else 0)

# Round float columns to int
float_cols = ['latitude', 'longitude', 'price', 'minimum_nights', 'reviews_per_month',
              'calculated_host_listings_count', 'availability_365']
for col in float_cols:
    grouped[col] = grouped[col].round().astype(int)

# Convert other aggregated columns to int
int_cols = ['id', 'name', 'host_id', 'host_name', 'neighbourhood_group', 'room_type', 'number_of_reviews', 'last_review']
for col in int_cols:
    grouped[col] = grouped[col].astype(int)

# Reorder columns to match target schema
target_columns = ['neighbourhood', 'id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
                  'latitude', 'longitude', 'room_type', 'price', 'minimum_nights',
                  'number_of_reviews', 'last_review', 'reviews_per_month',
                  'calculated_host_listings_count', 'availability_365']

grouped = grouped[target_columns]

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)