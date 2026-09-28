import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)

result = df0[['Product', 'Price']].copy()
result['Price'] = result['Price'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)