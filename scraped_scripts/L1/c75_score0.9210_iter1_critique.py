import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

# Group by 'neighbourhood' and aggregate as per plan
agg_df = df0.groupby('neighbourhood').agg(
    id=('id', 'count'),
    name=('name', pd.Series.nunique),
    host_id=('host_id', pd.Series.nunique),
    host_name=('host_name', pd.Series.nunique),
    neighbourhood_group=('neighbourhood_group', pd.Series.nunique),
    latitude=('latitude', pd.Series.nunique),
    longitude=('longitude', pd.Series.nunique),
    room_type=('room_type', pd.Series.nunique),
    price=('price', 'sum'),
    minimum_nights=('minimum_nights', 'sum'),
    number_of_reviews=('number_of_reviews', 'sum'),
    last_review=('last_review', pd.Series.nunique),
    reviews_per_month=('reviews_per_month', pd.Series.nunique),
    calculated_host_listings_count=('calculated_host_listings_count', 'sum'),
    availability_365=('availability_365', 'sum')
).reset_index()

# Ensure all columns have correct types as per target schema
agg_df['neighbourhood'] = agg_df['neighbourhood'].astype(str)
int_cols = ['id', 'name', 'host_id', 'host_name', 'neighbourhood_group', 'latitude', 'longitude',
            'room_type', 'price', 'minimum_nights', 'number_of_reviews', 'last_review',
            'reviews_per_month', 'calculated_host_listings_count', 'availability_365']
agg_df[int_cols] = agg_df[int_cols].fillna(0).astype(int)

# Reorder columns to match target schema exactly
agg_df = agg_df[['neighbourhood', 'id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
                 'latitude', 'longitude', 'room_type', 'price', 'minimum_nights', 'number_of_reviews',
                 'last_review', 'reviews_per_month', 'calculated_host_listings_count', 'availability_365']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)