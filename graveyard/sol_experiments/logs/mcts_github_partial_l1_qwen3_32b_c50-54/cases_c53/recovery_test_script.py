import pandas as pd

src_path = 'autopipeline-benchmarks/github-pipelines/length1_53/test_0.csv'
df = pd.read_csv(src_path, index_col=0)
result = df.groupby('continent', as_index=False).agg(
    beer_servings=('beer_servings', 'mean'),
    spirit_servings=('spirit_servings', 'mean'),
    wine_servings=('wine_servings', 'mean'),
    total_litres_of_pure_alcohol=('total_litres_of_pure_alcohol', 'mean')
)
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts_recovery_test_val.csv', index=False)