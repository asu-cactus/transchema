import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

df = df0.copy()

int_cols = ['id', 'name', 'host_id', 'host_name', 'neighbourhood_group', 'latitude', 'longitude', 'room_type', 'price', 'minimum_nights', 'number_of_reviews', 'last_review', 'reviews_per_month', 'calculated_host_listings_count', 'availability_365']

for col in int_cols:
    if col in ['last_review', 'reviews_per_month']:
        if col == 'last_review':
            df[col] = pd.to_datetime(df[col], errors='coerce').view('int64') // 10**9
            df[col] = df[col].fillna(0).astype(int)
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

df = df[['neighbourhood'] + int_cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)