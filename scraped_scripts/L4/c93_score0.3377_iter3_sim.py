import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

source0['gender'] = source0['gender'].map({'M':1, 'F':4}).fillna(0).astype(int)
source0['age'] = pd.to_numeric(source0['age'], errors='coerce').fillna(0).astype(int)
source0['occupation'] = pd.to_numeric(source0['occupation'], errors='coerce').fillna(0).astype(int)
source0['zip'] = source0['zip'].astype(str).str.extract('(\d+)').fillna('0').astype(int)

df = source2.merge(source0, on='user_id', how='left')
df = df.merge(source1, on='movie_id', how='left')

df.rename(columns={
    'title_x': 'title_x',
    'genres_x': 'genres_x',
    'title': 'title_y',
    'genres': 'genres_y'
}, inplace=True)

df['title_x'] = df['movie_id'].astype(int)
df['genres_x'] = df['movie_id'].astype(int)

df = df[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)