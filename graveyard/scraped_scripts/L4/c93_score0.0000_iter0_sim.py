import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

grouped = df2.groupby('movie_id').size().reset_index(name='count')

merged_1 = pd.merge(df2, df0, on='user_id', how='inner')

merged_2 = pd.merge(merged_1, df1, on='movie_id', how='inner', suffixes=('_x', '_y'))

merged_2['gender'] = merged_2['gender'].map({'M':1, 'F':4}).fillna(0).astype(int)
merged_2['age'] = pd.to_numeric(merged_2['age'], errors='coerce').fillna(0).astype(int)
merged_2['occupation'] = pd.to_numeric(merged_2['occupation'], errors='coerce').fillna(0).astype(int)
merged_2['zip'] = merged_2['zip'].astype(str).str.extract('(\d+)').fillna('0').astype(int)

result = merged_2[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
                   'title_x', 'genres_x', 'title_y', 'genres_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)