import pandas as pd

source_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_0.csv", index_col=0)
source_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_1.csv", index_col=0)
source_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_2.csv", index_col=0)
source_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_3.csv", index_col=0)
source_4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_4.csv", index_col=0)
source_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_5.csv", index_col=0)
source_6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_6.csv", index_col=0)
source_7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_7.csv", index_col=0)
source_8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_8.csv", index_col=0)
source_9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_9.csv", index_col=0)
source_10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_10.csv", index_col=0)

joined = pd.merge(source_10, source_0, left_on='0', right_on='0', how='inner')

result = joined.groupby('0', as_index=False).size().rename(columns={'size': '0'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_37/target_multisource_mcts.csv", index=False)