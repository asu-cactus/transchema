import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv", index_col=0)

# Group by 'sex' and 'smoker' and aggregate tip_pct by mean
df = df0.groupby(['sex', 'smoker'], as_index=False)['tip_pct'].mean()

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)