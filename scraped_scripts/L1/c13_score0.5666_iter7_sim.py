import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv", index_col=0)

result = df[['sex', 'smoker', 'tip_pct']].copy()
result['sex'] = result['sex'].astype(str)
result['smoker'] = result['smoker'].astype(str)
result['tip_pct'] = result['tip_pct'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)