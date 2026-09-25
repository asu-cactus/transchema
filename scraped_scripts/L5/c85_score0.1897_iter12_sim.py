import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_1.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_4.csv", index_col=0)

union_0_1 = pd.concat([s0, s1], ignore_index=True, sort=False)
union_0_1_4 = pd.concat([s4, union_0_1], ignore_index=True, sort=False)

result = union_0_1_4[['Sales']].copy()
result['Sales'] = result['Sales'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_85/target_multisource_mcts.csv", index=False)