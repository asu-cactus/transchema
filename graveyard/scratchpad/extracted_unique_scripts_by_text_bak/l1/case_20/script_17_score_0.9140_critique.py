import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv", index_col=0)

df = df0[['sex', 'smoker', 'total_bill', 'tip', 'size']].copy()

df['sex'] = df['sex'].astype(str)
df['smoker'] = df['smoker'].astype(str)
df['total_bill'] = df['total_bill'].astype(float)
df['tip'] = df['tip'].astype(float)
df['size'] = df['size'].astype(float)

df_grouped = df.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)