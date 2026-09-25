import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_4/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_4/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_4/training_2.csv", index_col=0)

union_result = pd.concat([source0, source1, source2], ignore_index=True)
target = union_result[['SN', 'Price']].copy()
target['SN'] = target['SN'].astype(str)
target['Price'] = target['Price'].astype(float)

target.to_csv("autopipeline-benchmarks/github-pipelines/length3_4/target_multisource_mcts.csv", index=False)