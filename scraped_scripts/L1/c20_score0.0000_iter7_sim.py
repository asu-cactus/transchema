import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_20/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_20/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_20/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

grouped = df.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

grouped['sex'] = grouped['sex'].astype(str)
grouped['smoker'] = grouped['smoker'].astype(str)
grouped['total_bill'] = grouped['total_bill'].astype(float)
grouped['tip'] = grouped['tip'].astype(float)
grouped['size'] = grouped['size'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)