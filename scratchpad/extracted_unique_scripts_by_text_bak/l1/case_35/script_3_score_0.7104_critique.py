import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv", index_col=0)

# First aggregate counts per ('Source Zipcode', 'NAICS Code Description') to remove duplicates
df_agg = df0.groupby(['Source Zipcode', 'NAICS Code Description'], as_index=False)['Counts'].sum()

# Then aggregate counts per 'Source Zipcode'
result = df_agg.groupby('Source Zipcode', as_index=False)['Counts'].sum()

result['Source Zipcode'] = result['Source Zipcode'].astype(int)
result['Counts'] = result['Counts'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)