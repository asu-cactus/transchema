import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_2.csv", index_col=0)

grouped = df1.groupby('movie_id', as_index=False).agg({'movie_id':'first'})

join1 = pd.merge(grouped, df1, on='movie_id', how='inner')

join2 = pd.merge(join1, df0, on='user_id', how='inner')

join3 = pd.merge(join2, df2, on='movie_id', how='inner')

join3['movie_title_x'] = join3['movie_title'].astype('category').cat.codes
join3['year_x'] = pd.to_numeric(join3['year'], errors='coerce').fillna(0).astype(int)

join3['movie_title_y'] = join3['movie_title']
join3['year_y'] = join3['year'].astype(str)

join3['age'] = join3['age'].astype(int)
join3['rating'] = join3['rating'].astype(int)
join3['timestamp'] = join3['timestamp'].astype(int)
join3['user_id'] = join3['user_id'].astype(int)
join3['movie_id'] = join3['movie_id'].astype(int)

join3['gender'] = join3['gender'].map({'M':1, 'F':2}).fillna(0).astype(int)

occupation_codes = {occ: i+1 for i, occ in enumerate(join3['occupation'].dropna().unique())}
join3['occupation'] = join3['occupation'].map(occupation_codes).fillna(0).astype(int)

join3['zip'] = pd.to_numeric(join3['zip'], errors='coerce').fillna(0).astype(int)

result = join3[['movie_id', 'movie_title_x', 'year_x', 'user_id', 'rating', 'timestamp', 'age', 'gender', 'occupation', 'zip', 'movie_title_y', 'year_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_10/target_multisource_mcts.csv", index=False)