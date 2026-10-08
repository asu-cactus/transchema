import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_12/training_0.csv", index_col=0)

result = df0.groupby(['SN', 'Price'], as_index=False).agg(count=('Purchase ID', 'count'))

result['SN'] = result['SN'].astype(str)
result['Price'] = result['Price'].astype(float)
result['count'] = result['count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_12/target_multisource_mcts.csv", index=False)