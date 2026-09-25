import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_1.csv", index_col=0)

# Join Source3_22_0 and Source3_22_1 on First Room = Room
df_joined = pd.merge(df0, df1, left_on='First Room', right_on='Room', how='inner')

# Aggregate sum of Reg Count by Department and Term
# We pivot Term values 20153, 20161, 20162 into columns with sum(Reg Count)
agg_df = df_joined.groupby(['Department', 'Term'], as_index=False)['Reg Count'].sum()

# Pivot Term to columns
pivot_df = agg_df.pivot(index='Department', columns='Term', values='Reg Count').reset_index()

# Rename columns to match target schema
pivot_df.columns.name = None  # remove the name of columns index
pivot_df = pivot_df.rename(columns={20153: '20153', 20161: '20161', 20162: '20162'})

# If any of the term columns are missing (no data), fill with 0
for col in ['20153', '20161', '20162']:
    if col not in pivot_df.columns:
        pivot_df[col] = 0

# Reorder columns to match target schema
pivot_df = pivot_df[['Department', '20153', '20161', '20162']]

# Convert to float as in target schema
pivot_df['20153'] = pivot_df['20153'].astype(float)
pivot_df['20161'] = pivot_df['20161'].astype(float)
pivot_df['20162'] = pivot_df['20162'].astype(float)

pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)