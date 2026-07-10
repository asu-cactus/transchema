import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_2.csv", index_col=0)

# Select relevant columns and ensure correct types
cols = ['sex', 'smoker', 'total_bill', 'tip', 'size']
df0 = df0[cols].copy()
df1 = df1[cols].copy()
df2 = df2[cols].copy()

for df in [df0, df1, df2]:
    df['sex'] = df['sex'].astype(str)
    df['smoker'] = df['smoker'].astype(str)
    df['total_bill'] = df['total_bill'].astype(float)
    df['tip'] = df['tip'].astype(float)
    df['size'] = df['size'].astype(float)

# UNION all source tables
df = pd.concat([df0, df1, df2], ignore_index=True)

# GROUP BY 'sex' and 'smoker' and aggregate numerical columns by mean
result = df.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)