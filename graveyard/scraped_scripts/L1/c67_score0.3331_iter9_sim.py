import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)

union_result = pd.concat([df0, df1], ignore_index=True)

joined = pd.merge(union_result, union_result, on="user_id", suffixes=('_left', '_right'))

result = pd.DataFrame()
result['user_id'] = joined['user_id']
result['sad'] = joined['sad.depressed_left'].astype(float)
result['stressed'] = joined['open.stressed_left'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)