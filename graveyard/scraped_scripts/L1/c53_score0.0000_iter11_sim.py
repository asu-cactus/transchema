import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_53/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_53/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

result = df.groupby("continent", as_index=False).agg({
    "beer_servings": "mean",
    "spirit_servings": "mean",
    "wine_servings": "mean",
    "total_litres_of_pure_alcohol": "mean"
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts.csv", index=False)