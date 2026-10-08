import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_53/training_0.csv", index_col=0)
df = df[(df['continent'].notnull()) & (df['continent'] != '')]
df = df[['continent', 'beer_servings', 'spirit_servings', 'wine_servings', 'total_litres_of_pure_alcohol']]
df = df.astype({
    'continent': str,
    'beer_servings': float,
    'spirit_servings': float,
    'wine_servings': float,
    'total_litres_of_pure_alcohol': float
})
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts.csv", index=False)