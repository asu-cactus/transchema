import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_20/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_20/training_2.csv', index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

df = df[['sex', 'smoker', 'total_bill', 'tip', 'size']]

df['sex'] = df['sex'].astype(str)
df['smoker'] = df['smoker'].astype(str)
df['total_bill'] = df['total_bill'].astype(float)
df['tip'] = df['tip'].astype(float)
df['size'] = df['size'].astype(float)

df = df.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

df.to_csv('autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv', index=False)