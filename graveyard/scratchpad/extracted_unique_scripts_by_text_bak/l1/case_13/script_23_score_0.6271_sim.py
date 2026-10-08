import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv", index_col=0)

df = pd.concat([df0], ignore_index=True)

df = df[['sex', 'smoker', 'tip_pct']]

df['sex'] = df['sex'].astype(str)
df['smoker'] = df['smoker'].astype(str)
df['tip_pct'] = df['tip_pct'].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)