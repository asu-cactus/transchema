import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_66/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_66/training_1.csv", index_col=0)

result = df1[['school_name', 'reading_score']].copy()
result['reading_score'] = pd.to_numeric(result['reading_score'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_66/target_multisource_mcts.csv", index=False)