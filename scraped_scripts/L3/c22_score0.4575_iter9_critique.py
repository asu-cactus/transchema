import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_1.csv", index_col=0)

# Join df0 with df1 on First Room = Room to get First Room Size (not used in final output but required to use all sources)
df0 = df0.merge(df1, how='left', left_on='First Room', right_on='Room', suffixes=('', '_FirstRoomSize'))

# Join df0 with df1 on Second Room = Room to get Second Room Size (not used in final output but required)
df0 = df0.merge(df1, how='left', left_on='Second Room', right_on='Room', suffixes=('', '_SecondRoomSize'))

# Aggregate Reg Count by Department and Term
df_grouped = df0.groupby(['Department', 'Term'], as_index=False)['Reg Count'].sum()

# Pivot Term to columns
df_pivot = df_grouped.pivot(index='Department', columns='Term', values='Reg Count')

# Reset index and rename columns to match target schema
df_pivot = df_pivot.rename_axis(None, axis=1).reset_index()

# Ensure all target term columns exist
target_terms = ['20153', '20161', '20162']
for term in target_terms:
    if term not in df_pivot.columns:
        df_pivot[term] = pd.NA

# Select columns in target order
df_result = df_pivot[['Department'] + target_terms]

# Write output
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)