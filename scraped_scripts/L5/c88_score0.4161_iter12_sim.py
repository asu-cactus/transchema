import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_88/training_4.csv", index_col=0)

result = pd.DataFrame()
result['Profit'] = [source2['Profit'].sum()]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_88/target_multisource_mcts.csv", index=False)