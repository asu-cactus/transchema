import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_95/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_95/training_1.csv", index_col=0)

union_df = pd.concat([df1, df2], ignore_index=True)
result = union_df[['school_name', 'math_score']].copy()
result['math_score'] = result['math_score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_95/target_multisource_mcts.csv", index=False)