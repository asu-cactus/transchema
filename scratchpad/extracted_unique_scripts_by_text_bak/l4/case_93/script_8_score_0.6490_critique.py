import pandas as pd
import re

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

# Join df2 and df0 on user_id
df_merged_0 = pd.merge(df2, df0, on="user_id", how="inner")

# Join the above result with df1 on movie_id
df_merged = pd.merge(df_merged_0, df1, on="movie_id", how="inner")

# Map gender to integer (M=1, F=2)
df_merged['gender'] = df_merged['gender'].map({'M': 1, 'F': 2}).astype(int)

# Convert zip to integer by removing non-digit characters
df_merged['zip'] = df_merged['zip'].astype(str).str.extract('(\d+)').astype(int)

# Create categorical codes for title and genres (from df1)
df_merged['title_x'] = df_merged['title'].astype('category').cat.codes.astype(int)
df_merged['genres_x'] = df_merged['genres'].astype('category').cat.codes.astype(int)

# Select and rename columns to match target schema
result = df_merged[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
                    'title_x', 'genres_x', 'title', 'genres']]

result = result.rename(columns={'title': 'title_y', 'genres': 'genres_y'})

# Ensure correct dtypes for integer columns
int_cols = ['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x']
result[int_cols] = result[int_cols].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)