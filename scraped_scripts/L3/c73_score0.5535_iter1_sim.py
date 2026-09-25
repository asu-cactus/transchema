import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_73/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_73/training_1.csv", index_col=0)

df = pd.concat([df1, df2], ignore_index=True)

result = df[['city', 'fare']].copy()
result['type'] = 'Urban'
result['fare'] = result['fare'].astype(float)
result = result[['city', 'type', 'fare']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_73/target_multisource_mcts.csv", index=False)