import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_89/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_89/training_1.csv", index_col=0)

df0_proj = df0[['city', 'fare']].copy()
df1_proj = df1[['city']].copy()
df1_proj['fare'] = pd.NA

result = pd.concat([df0_proj, df1_proj], ignore_index=True)
result['fare'] = pd.to_numeric(result['fare'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_89/target_multisource_mcts.csv", index=False)