import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

# Group by 'neighbourhood' and aggregate count distinct for other columns
agg_dict = {
    'id': pd.Series.nunique,
    'name': pd.Series.nunique,
    'host_id': pd.Series.nunique,
    'host_name': pd.Series.nunique,
    'neighbourhood_group': pd.Series.nunique,
    'latitude': pd.Series.nunique,
    'longitude': pd.Series.nunique,
    'room_type': pd.Series.nunique,
    'price': pd.Series.nunique,
    'minimum_nights': pd.Series.nunique,
    'number_of_reviews': pd.Series.nunique,
    'last_review': pd.Series.nunique,
    'reviews_per_month': pd.Series.nunique,
    'calculated_host_listings_count': pd.Series.nunique,
    'availability_365': pd.Series.nunique
}

df_agg = df0.groupby('neighbourhood').agg(agg_dict).reset_index()

# Ensure columns order matches target schema
df_agg = df_agg[['neighbourhood', 'id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
                 'latitude', 'longitude', 'room_type', 'price', 'minimum_nights',
                 'number_of_reviews', 'last_review', 'reviews_per_month',
                 'calculated_host_listings_count', 'availability_365']]

# Convert all columns except 'neighbourhood' to int (they are counts)
for col in df_agg.columns:
    if col != 'neighbourhood':
        df_agg[col] = df_agg[col].astype(int)

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)