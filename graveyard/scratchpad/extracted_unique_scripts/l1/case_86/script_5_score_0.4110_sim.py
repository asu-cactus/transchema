import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

df_union = pd.concat([df0, df0], ignore_index=True)

result = df_union[['neighbourhood', 'price']].copy()
result.rename(columns={'price': 'price_24'}, inplace=True)
result['price_24'] = result['price_24'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)