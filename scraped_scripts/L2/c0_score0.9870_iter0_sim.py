import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_0/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_0/training_1.csv", index_col=0)

merged = pd.merge(source1, source0[['school_name']], on='school_name')

result = merged.groupby('school_name', as_index=False)['reading_score'].mean()
result['reading_score'] = result['reading_score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_0/target_multisource_mcts.csv", index=False)