import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="movieId")

pivoted = joined.pivot_table(index="movieId", values="rating_x", aggfunc='mean')

pivoted = pivoted.rename(columns={"rating_x": "rating"}).reset_index()

pivoted["movieId"] = pivoted["movieId"].astype(int)
pivoted["rating"] = pivoted["rating"].astype(float)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_57/target_multisource_mcts.csv", index=False)