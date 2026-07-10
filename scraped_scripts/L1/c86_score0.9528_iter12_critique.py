import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

result = df0.groupby('neighbourhood', as_index=False).agg({'id': 'count'}).rename(columns={'id': 'price_24'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)