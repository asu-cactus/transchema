import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

# Group by 'neighbourhood' and aggregate by count distinct for other columns
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

df_target = df.groupby('neighbourhood').agg(agg_dict).reset_index()

# Cast all columns to int as per target schema
for col in df_target.columns:
    if col != 'neighbourhood':
        df_target[col] = df_target[col].astype(int)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)