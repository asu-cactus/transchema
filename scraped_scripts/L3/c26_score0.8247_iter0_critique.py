import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_2.csv", index_col=0)

# Join Source0 and Source1 on movie_id
df01 = pd.merge(df0, df1[["movie_id", "title"]], on="movie_id", how="inner")

# Join the above with Source2 on user_id
df_all = pd.merge(df01, df2, on="user_id", how="inner")

# Group by title and compute mean rating
grouped = df_all.groupby("title", as_index=False)["rating"].mean()

# Normalize ratings by subtracting global mean rating
global_mean = grouped["rating"].mean()
grouped["0"] = grouped["rating"] - global_mean

result = grouped[["title", "0"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_26/target_multisource_mcts.csv", index=False)