import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_2.csv", index_col=0)

# Join df0 and df1 on movie_id
df01 = pd.merge(df0, df1, on="movie_id")

# Join the above with df2 on user_id
df_all = pd.merge(df01, df2, on="user_id")

# Group by title and compute mean rating
df_grouped = df_all.groupby("title", as_index=False)["rating"].mean()

# Normalize the mean ratings (z-score normalization)
mean_rating = df_grouped["rating"].mean()
std_rating = df_grouped["rating"].std()
df_grouped["0"] = (df_grouped["rating"] - mean_rating) / std_rating

# Keep only the required columns with exact target schema
df_result = df_grouped[["title", "0"]]

# Write output
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_26/target_multisource_mcts.csv", index=False)