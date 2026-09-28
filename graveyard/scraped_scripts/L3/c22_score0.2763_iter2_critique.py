import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_1.csv", index_col=0)

# Join on First Room = Room (inner join)
df_joined = pd.merge(df0, df1, left_on='First Room', right_on='Room', how='inner')

# Filter Term to only those in target schema
valid_terms = [20153, 20161, 20162]
df_filtered = df_joined[df_joined['Term'].isin(valid_terms)]

# Group by Department and Term, sum Reg Count
agg = df_filtered.groupby(['Department', 'Term'], as_index=False)['Reg Count'].sum()

# Pivot Term to columns named as strings
pivot = agg.pivot(index='Department', columns='Term', values='Reg Count')

# Rename columns to strings matching target schema
pivot = pivot.rename(columns={20153: '20153', 20161: '20161', 20162: '20162'})

# Reset index to get Department as a column
result = pivot.reset_index()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)