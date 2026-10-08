import pandas as pd

# Read the single source file given
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv", index_col=0)

# Select relevant columns and ensure correct types
df = df0[['sex', 'smoker', 'total_bill', 'tip', 'size']].copy()
df['sex'] = df['sex'].astype(str)
df['smoker'] = df['smoker'].astype(str)
df['total_bill'] = df['total_bill'].astype(float)
df['tip'] = df['tip'].astype(float)
df['size'] = df['size'].astype(float)

# Group by 'sex' and 'smoker' and aggregate by mean for numeric columns
df_grouped = df.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

# Write output with exact target schema and no index
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)