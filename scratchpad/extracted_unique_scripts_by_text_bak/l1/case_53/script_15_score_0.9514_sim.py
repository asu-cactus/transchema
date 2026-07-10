import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_53/training_0.csv", index_col=0)

result = df.groupby('continent', as_index=False).agg({
    'beer_servings': 'mean',
    'spirit_servings': 'mean',
    'wine_servings': 'mean',
    'total_litres_of_pure_alcohol': 'mean'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts.csv", index=False)