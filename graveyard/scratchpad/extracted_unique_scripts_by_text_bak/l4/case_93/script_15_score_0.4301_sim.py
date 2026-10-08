import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

df0['gender'] = df0['gender'].map({'M': 1, 'F': 2}).fillna(0).astype(int)
df0['zip'] = df0['zip'].str.extract('(\d+)').fillna('0').astype(int)

pivot = df0.pivot_table(index='user_id', columns='gender', values='age', aggfunc='first').fillna(0).astype(int)
pivot.columns = [f'gender_{int(col)}' for col in pivot.columns]

pivot_age = df0.groupby('user_id')['age'].first().astype(int)
pivot_occupation = df0.groupby('user_id')['occupation'].first().astype(int)
pivot_zip = df0.groupby('user_id')['zip'].first().astype(int)
pivot_gender = df0.groupby('user_id')['gender'].first().astype(int)

pivot_df = pd.DataFrame({
    'user_id': pivot_age.index,
    'gender': pivot_gender.values,
    'age': pivot_age.values,
    'occupation': pivot_occupation.values,
    'zip': pivot_zip.values
})

df = df2.merge(pivot_df, on='user_id', how='left')
df = df.merge(df1, on='movie_id', how='left')

df['title_x'] = df['title'].factorize()[0] + 1
df['genres_x'] = df['genres'].factorize()[0] + 1
df['title_y'] = df['title']
df['genres_y'] = df['genres']

df = df[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)