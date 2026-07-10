import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_20/training_0.csv", index_col=0)

joined = pd.merge(source0, source0, left_on="Item ID", right_on="Item ID", suffixes=('_left', '_right'))

result = joined[['SN_left', 'Price_left']].copy()
result.columns = ['SN', 'Price']
result['SN'] = result['SN'].astype(str)
result['Price'] = result['Price'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_20/target_multisource_mcts.csv", index=False)