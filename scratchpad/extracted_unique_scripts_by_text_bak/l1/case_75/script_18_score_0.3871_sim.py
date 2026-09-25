import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

df_target = pd.DataFrame()
df_target['neighbourhood'] = df['neighbourhood'].astype(str)
df_target['id'] = df['id'].astype(int)
df_target['name'] = pd.to_numeric(df['name'], errors='coerce').fillna(df['name'].astype('category').cat.codes).astype(int)
df_target['host_id'] = df['host_id'].astype(int)
df_target['host_name'] = pd.to_numeric(df['host_name'], errors='coerce').fillna(df['host_name'].astype('category').cat.codes).astype(int)
df_target['neighbourhood_group'] = pd.to_numeric(df['neighbourhood_group'], errors='coerce').fillna(df['neighbourhood_group'].astype('category').cat.codes).astype(int)
df_target['latitude'] = df['latitude'].astype(int)
df_target['longitude'] = df['longitude'].astype(int)
df_target['room_type'] = pd.to_numeric(df['room_type'], errors='coerce').fillna(df['room_type'].astype('category').cat.codes).astype(int)
df_target['price'] = df['price'].astype(int)
df_target['minimum_nights'] = df['minimum_nights'].astype(int)
df_target['number_of_reviews'] = df['number_of_reviews'].astype(int)
df_target['last_review'] = pd.to_datetime(df['last_review'], errors='coerce').map(lambda x: x.toordinal() if pd.notnull(x) else 0).astype(int)
df_target['reviews_per_month'] = pd.to_numeric(df['reviews_per_month'], errors='coerce').fillna(0).astype(int)
df_target['calculated_host_listings_count'] = df['calculated_host_listings_count'].astype(int)
df_target['availability_365'] = df['availability_365'].astype(int)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)