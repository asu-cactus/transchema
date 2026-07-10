import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv", index_col=0)

df0['sex'] = df0['sex'].astype(str)
df0['smoker'] = df0['smoker'].astype(str)
df0['total_bill'] = df0['total_bill'].astype(float)
df0['tip'] = df0['tip'].astype(float)
df0['size'] = df0['size'].astype(float)

result = df0.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)