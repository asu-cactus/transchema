import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

df['id'] = df['id'].astype(int)
df['name'] = pd.to_numeric(df['name'], errors='coerce').fillna(0).astype(int)
df['host_id'] = pd.to_numeric(df['host_id'], errors='coerce').fillna(0).astype(int)
df['host_name'] = pd.to_numeric(df['host_name'], errors='coerce').fillna(0).astype(int)
df['neighbourhood_group'] = pd.to_numeric(df['neighbourhood_group'], errors='coerce').fillna(0).astype(int)
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0).astype(int)
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0).astype(int)
df['room_type'] = pd.to_numeric(df['room_type'], errors='coerce').fillna(0).astype(int)
df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)
df['minimum_nights'] = pd.to_numeric(df['minimum_nights'], errors='coerce').fillna(0).astype(int)
df['number_of_reviews'] = pd.to_numeric(df['number_of_reviews'], errors='coerce').fillna(0).astype(int)
df['last_review'] = pd.to_numeric(df['last_review'], errors='coerce').fillna(0).astype(int)
df['reviews_per_month'] = pd.to_numeric(df['reviews_per_month'], errors='coerce').fillna(0).astype(int)
df['calculated_host_listings_count'] = pd.to_numeric(df['calculated_host_listings_count'], errors='coerce').fillna(0).astype(int)
df['availability_365'] = pd.to_numeric(df['availability_365'], errors='coerce').fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)