import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv", index_col=0)
df = df0[['sex', 'smoker', 'tip_pct']].copy()
df['sex'] = df['sex'].astype(str)
df['smoker'] = df['smoker'].astype(str)
df['tip_pct'] = df['tip_pct'].astype(float)

# Group by sex and smoker, aggregate tip_pct by mean
df_grouped = df.groupby(['sex', 'smoker'], as_index=False).agg({'tip_pct': 'mean'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)