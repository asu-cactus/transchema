import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_95/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_95/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, how='inner', left_on='school_name', right_on='school_name')

result = merged[['school_name', 'math_score']].copy()
result['school_name'] = result['school_name'].astype(str)
result['math_score'] = pd.to_numeric(result['math_score'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_95/target_multisource_mcts.csv", index=False)