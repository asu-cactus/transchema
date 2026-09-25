import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_1.csv", index_col=0)

# Join df0 with df1 on First Room to get Size for First Room
df_join1 = pd.merge(df0, df1, how='left', left_on='First Room', right_on='Room', suffixes=('', '_FirstRoomSize'))

# Rename Size column from df1 to FirstRoomSize
df_join1 = df_join1.rename(columns={'Size': 'FirstRoomSize'})

# Drop redundant 'Room' column from df1 after join
df_join1 = df_join1.drop(columns=['Room'])

# Join the above result with df1 again on Second Room to get Size for Second Room
df_join2 = pd.merge(df_join1, df1, how='left', left_on='Second Room', right_on='Room', suffixes=('', '_SecondRoomSize'))

# Rename Size column from df1 to SecondRoomSize
df_join2 = df_join2.rename(columns={'Size': 'SecondRoomSize'})

# Drop redundant 'Room' column from second join
df_join2 = df_join2.drop(columns=['Room'])

# Fill NaN sizes with 0 (rooms may be missing)
df_join2['FirstRoomSize'] = df_join2['FirstRoomSize'].fillna(0)
df_join2['SecondRoomSize'] = df_join2['SecondRoomSize'].fillna(0)

# Now aggregate sum of Reg Count per Department and Term
agg = df_join2.groupby(['Department', 'Term'], as_index=False).agg({'Reg Count': 'sum'})

# Pivot Term to columns 20153, 20161, 20162
pivot = agg.pivot(index='Department', columns='Term', values='Reg Count')

# Rename columns to strings as in target schema
pivot.columns = pivot.columns.astype(str)

# Ensure all target term columns exist, fill missing with 0
for col in ['20153', '20161', '20162']:
    if col not in pivot.columns:
        pivot[col] = 0.0

# Reorder columns as per target schema
pivot = pivot[['20153', '20161', '20162']]

# Reset index to have Department as a column
pivot = pivot.reset_index()

# Convert columns to float as in target schema
pivot['20153'] = pivot['20153'].astype(float)
pivot['20161'] = pivot['20161'].astype(float)
pivot['20162'] = pivot['20162'].astype(float)

# Write output
pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)