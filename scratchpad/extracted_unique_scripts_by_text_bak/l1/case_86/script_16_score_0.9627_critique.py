import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

# Group by 'neighbourhood' and aggregate mean of 'price'
result = df0.groupby('neighbourhood', as_index=False)['price'].mean()

# Rename column to match target schema
result.rename(columns={'price': 'price_24'}, inplace=True)

# Convert price_24 to integer type (rounding)
result['price_24'] = result['price_24'].round().astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)