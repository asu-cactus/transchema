import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_53/training_0.csv", index_col=0)
df = df[['continent', 'beer_servings', 'spirit_servings', 'wine_servings', 'total_litres_of_pure_alcohol']]
df['beer_servings'] = df['beer_servings'].astype(float)
df['spirit_servings'] = df['spirit_servings'].astype(float)
df['wine_servings'] = df['wine_servings'].astype(float)
df['total_litres_of_pure_alcohol'] = df['total_litres_of_pure_alcohol'].astype(float)
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts.csv", index=False)