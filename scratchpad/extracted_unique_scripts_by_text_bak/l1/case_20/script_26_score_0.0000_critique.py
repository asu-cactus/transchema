import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_20/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_20/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_20/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df = df[['sex', 'smoker', 'total_bill', 'tip', 'size']]

df['sex'] = df['sex'].astype(str)
df['smoker'] = df['smoker'].astype(str)
df['total_bill'] = df['total_bill'].astype(float)
df['tip'] = df['tip'].astype(float)
df['size'] = df['size'].astype(float)

# Group by 'sex' and 'smoker' and aggregate numeric columns by mean
df = df.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)