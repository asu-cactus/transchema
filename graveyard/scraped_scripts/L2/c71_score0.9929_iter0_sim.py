import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_71/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_71/training_1.csv", index_col=0)

merged = pd.merge(source1, source0[['school_name', 'type']], on='school_name')

result = merged.groupby('type', as_index=False)['reading_score'].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_71/target_multisource_mcts.csv", index=False)