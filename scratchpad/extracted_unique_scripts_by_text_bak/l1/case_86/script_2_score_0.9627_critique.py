import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

df = df0.groupby('neighbourhood', as_index=False)['price'].mean()
df.rename(columns={'price': 'price_24'}, inplace=True)
df['price_24'] = df['price_24'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)