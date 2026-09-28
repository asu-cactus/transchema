import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_66/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_66/training_1.csv", index_col=0)

df_union = pd.concat([df1, df2], ignore_index=True)
result = df_union[['school_name', 'reading_score']].copy()
result['reading_score'] = result['reading_score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_66/target_multisource_mcts.csv", index=False)