import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_2.csv", index_col=0)

# Join user info with ratings on user_id
df01 = pd.merge(df0, df1, how="inner", on="user_id")

# Join with movies on movie_id
df012 = pd.merge(df01, df2, how="inner", on="movie_id")

# Group by title and gender, aggregate mean rating
grouped = df012.groupby(['title', 'gender'])['rating'].mean().reset_index()

# Pivot to get columns F and M for genders
pivot = grouped.pivot(index='title', columns='gender', values='rating').reset_index()

# Merge with full movie list to keep all titles
result = pd.merge(df2[['title']], pivot, how='left', on='title')

# Ensure columns F and M exist, fill missing with NaN (or 0 if needed)
result = result.rename(columns={'F': 'F', 'M': 'M'})
result = result[['title', 'F', 'M']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_16/target_multisource_mcts.csv", index=False)