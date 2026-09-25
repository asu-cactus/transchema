import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

# Convert columns to appropriate types
df['neighbourhood'] = df['neighbourhood'].astype(str)
df['id'] = pd.to_numeric(df['id'], errors='coerce')
df['name'] = df['name'].astype(str)
df['host_id'] = pd.to_numeric(df['host_id'], errors='coerce')
df['host_name'] = df['host_name'].astype(str)
df['neighbourhood_group'] = df['neighbourhood_group'].astype(str)
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df['room_type'] = df['room_type'].astype(str)
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['minimum_nights'] = pd.to_numeric(df['minimum_nights'], errors='coerce')
df['number_of_reviews'] = pd.to_numeric(df['number_of_reviews'], errors='coerce')
df['last_review'] = df['last_review'].astype(str)
df['reviews_per_month'] = pd.to_numeric(df['reviews_per_month'], errors='coerce')
df['calculated_host_listings_count'] = pd.to_numeric(df['calculated_host_listings_count'], errors='coerce')
df['availability_365'] = pd.to_numeric(df['availability_365'], errors='coerce')

# Define aggregation functions
agg_dict = {
    'id': pd.Series.nunique,
    'name': lambda x: x.nunique(),
    'host_id': pd.Series.nunique,
    'host_name': lambda x: x.nunique(),
    'neighbourhood_group': lambda x: x.nunique(),
    'latitude': 'mean',
    'longitude': 'mean',
    'room_type': lambda x: x.nunique(),
    'price': 'mean',
    'minimum_nights': 'mean',
    'number_of_reviews': 'mean',
    'last_review': lambda x: x.nunique(),
    'reviews_per_month': 'mean',
    'calculated_host_listings_count': 'mean',
    'availability_365': 'mean'
}

df_out = df.groupby('neighbourhood').agg(agg_dict).reset_index()

# Round mean columns to int
mean_cols = ['latitude', 'longitude', 'price', 'minimum_nights', 'number_of_reviews',
             'reviews_per_month', 'calculated_host_listings_count', 'availability_365']

for col in mean_cols:
    df_out[col] = df_out[col].round().astype(int)

# Convert count distinct columns to int
count_distinct_cols = ['id', 'name', 'host_id', 'host_name', 'neighbourhood_group', 'room_type', 'last_review']
for col in count_distinct_cols:
    df_out[col] = df_out[col].astype(int)

# Ensure column order matches target schema
df_out = df_out[['neighbourhood', 'id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
                 'latitude', 'longitude', 'room_type', 'price', 'minimum_nights',
                 'number_of_reviews', 'last_review', 'reviews_per_month',
                 'calculated_host_listings_count', 'availability_365']]

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)