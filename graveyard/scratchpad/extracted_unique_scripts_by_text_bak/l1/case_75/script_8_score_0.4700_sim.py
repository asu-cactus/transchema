import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

df_out = pd.DataFrame()
df_out['neighbourhood'] = df['neighbourhood'].astype(str)
df_out['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
df_out['name'] = pd.to_numeric(df['name'], errors='coerce').fillna(0).astype(int)
df_out['host_id'] = pd.to_numeric(df['host_id'], errors='coerce').fillna(0).astype(int)
df_out['host_name'] = pd.to_numeric(df['host_name'], errors='coerce').fillna(0).astype(int)
df_out['neighbourhood_group'] = pd.to_numeric(df['neighbourhood_group'], errors='coerce').fillna(0).astype(int)
df_out['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0).astype(int)
df_out['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0).astype(int)
df_out['room_type'] = pd.to_numeric(df['room_type'], errors='coerce').fillna(0).astype(int)
df_out['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)
df_out['minimum_nights'] = pd.to_numeric(df['minimum_nights'], errors='coerce').fillna(0).astype(int)
df_out['number_of_reviews'] = pd.to_numeric(df['number_of_reviews'], errors='coerce').fillna(0).astype(int)
df_out['last_review'] = pd.to_numeric(df['last_review'], errors='coerce').fillna(0).astype(int)
df_out['reviews_per_month'] = pd.to_numeric(df['reviews_per_month'], errors='coerce').fillna(0).astype(int)
df_out['calculated_host_listings_count'] = pd.to_numeric(df['calculated_host_listings_count'], errors='coerce').fillna(0).astype(int)
df_out['availability_365'] = pd.to_numeric(df['availability_365'], errors='coerce').fillna(0).astype(int)

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)