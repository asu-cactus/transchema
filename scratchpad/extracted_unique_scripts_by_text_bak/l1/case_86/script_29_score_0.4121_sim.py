import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)
result = df0[['neighbourhood', 'price']].copy()
result.rename(columns={'price': 'price_24'}, inplace=True)
result['price_24'] = result['price_24'].astype('Int64')
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)