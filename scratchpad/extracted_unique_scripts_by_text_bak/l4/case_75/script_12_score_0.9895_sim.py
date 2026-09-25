import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_1.csv", index_col=0)

agg = source1.groupby('school_name')[['reading_score', 'math_score']].mean().reset_index()

merged = pd.merge(agg, source0[['school_name', 'type']], on='school_name', how='left')

result = merged.groupby('type')[['reading_score', 'math_score']].mean().reset_index()

result = result.rename(columns={'reading_score': 'a', 'math_score': 'b'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)