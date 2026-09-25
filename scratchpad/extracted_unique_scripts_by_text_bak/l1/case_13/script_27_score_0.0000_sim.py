import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_13/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_13/training_2.csv', index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

result = df[['sex', 'smoker', 'tip_pct']].copy()
result['sex'] = result['sex'].astype(str)
result['smoker'] = result['smoker'].astype(str)
result['tip_pct'] = result['tip_pct'].astype(float)

result.to_csv('autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv', index=False)