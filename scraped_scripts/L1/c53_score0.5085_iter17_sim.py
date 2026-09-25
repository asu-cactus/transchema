import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_53/training_0.csv", index_col=0)
df = df[df["total_litres_of_pure_alcohol"] > 0]
df = df[["continent", "beer_servings", "spirit_servings", "wine_servings", "total_litres_of_pure_alcohol"]]
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts.csv", index=False)