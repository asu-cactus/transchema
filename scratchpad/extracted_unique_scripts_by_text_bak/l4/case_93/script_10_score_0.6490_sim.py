import pandas as pd

s0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv', index_col=0)
s1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv', index_col=0)
s2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv', index_col=0)

s0['gender'] = s0['gender'].map({'M':1, 'F':2}).fillna(0).astype(int)
s0['zip'] = s0['zip'].astype(str).str.extract(r'(\d{5})')[0]
s0['zip'] = pd.to_numeric(s0['zip'], errors='coerce').fillna(0).astype(int)

join_1 = pd.merge(s2, s0, on='user_id', how='inner')

s1_encoded = s1.copy()
s1_encoded['title_x'] = pd.factorize(s1_encoded['title'])[0] + 1
s1_encoded['genres_x'] = pd.factorize(s1_encoded['genres'])[0] + 1
s1_encoded = s1_encoded[['movie_id', 'title_x', 'genres_x']]

join_2 = pd.merge(join_1, s1_encoded, on='movie_id', how='inner')

join_3 = pd.merge(join_2, s1[['movie_id', 'title', 'genres']], on='movie_id', how='inner')

join_3 = join_3.rename(columns={'title': 'title_y', 'genres': 'genres_y'})

result = join_3[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
                 'title_x', 'genres_x', 'title_y', 'genres_y']]

result['movie_id'] = result['movie_id'].astype(int)
result['user_id'] = result['user_id'].astype(int)
result['rating'] = result['rating'].astype(int)
result['timestamp'] = result['timestamp'].astype(int)
result['gender'] = result['gender'].astype(int)
result['age'] = result['age'].astype(int)
result['occupation'] = result['occupation'].astype(int)
result['zip'] = result['zip'].astype(int)
result['title_x'] = result['title_x'].astype(int)
result['genres_x'] = result['genres_x'].astype(int)
result['title_y'] = result['title_y'].astype(str)
result['genres_y'] = result['genres_y'].astype(str)

result.to_csv('autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv', index=False)