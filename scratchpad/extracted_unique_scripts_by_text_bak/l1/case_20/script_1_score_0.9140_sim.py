import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv", index_col=0)

grouped = df0.groupby(['sex', 'smoker'], as_index=False).agg({
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