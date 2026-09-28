import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_43/training_1.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

result = df.groupby("artist_name", as_index=False).agg({
    "speechiness": "mean",
    "instrumentalness": "mean",
    "danceability": "mean",
    "energy": "mean",
    "acousticness": "mean"
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_43/target_multisource_mcts.csv", index=False)