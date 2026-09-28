import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_13/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_13/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_13/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Select relevant columns and ensure correct types
df = df[['sex', 'smoker', 'tip_pct']].copy()
df['sex'] = df['sex'].astype(str)
df['smoker'] = df['smoker'].astype(str)
df['tip_pct'] = df['tip_pct'].astype(float)

# Group by sex and smoker, aggregate tip_pct by mean
result = df.groupby(['sex', 'smoker'], as_index=False).agg({'tip_pct': 'mean'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)