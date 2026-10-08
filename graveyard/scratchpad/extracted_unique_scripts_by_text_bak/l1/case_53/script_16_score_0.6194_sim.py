import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_53/training_0.csv", index_col=0)
df_filtered = df0[df0['continent'].notnull()]
df_result = df_filtered[['continent', 'beer_servings', 'spirit_servings', 'wine_servings', 'total_litres_of_pure_alcohol']].copy()
df_result['beer_servings'] = df_result['beer_servings'].astype(float)
df_result['spirit_servings'] = df_result['spirit_servings'].astype(float)
df_result['wine_servings'] = df_result['wine_servings'].astype(float)
df_result['total_litres_of_pure_alcohol'] = df_result['total_litres_of_pure_alcohol'].astype(float)
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts.csv")