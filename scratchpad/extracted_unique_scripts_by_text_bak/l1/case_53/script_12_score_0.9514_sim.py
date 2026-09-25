import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_53/training_0.csv", index_col=0)

result = df0.groupby('continent', as_index=False).agg({
    'beer_servings': 'mean',
    'spirit_servings': 'mean',
    'wine_servings': 'mean',
    'total_litres_of_pure_alcohol': 'mean'
})

result = result[['continent', 'beer_servings', 'spirit_servings', 'wine_servings', 'total_litres_of_pure_alcohol']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts.csv", index=False)