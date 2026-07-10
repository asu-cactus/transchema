import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)

union_result = pd.concat([df0, df1], ignore_index=True)
result = union_result[['crit_cn', 'critic']].copy()
result['crit_cn'] = result['crit_cn'].astype(str)
result['critic'] = pd.to_numeric(result['critic'], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)