import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_1.csv", index_col=0)

# Prepare first session dataframe by joining on First Room = Room
first_session = df0[['Department', 'Term', 'Reg Count', 'First Room']].copy()
first_session = first_session.merge(df1, left_on='First Room', right_on='Room', how='inner')
# Keep relevant columns
first_session = first_session[['Department', 'Term', 'Reg Count']]

# Prepare second session dataframe by joining on Second Room = Room
second_session = df0[['Department', 'Term', 'Reg Count', 'Second Room']].copy()
second_session = second_session.merge(df1, left_on='Second Room', right_on='Room', how='inner')
second_session = second_session[['Department', 'Term', 'Reg Count']]

# Union the two sessions
df_union = pd.concat([first_session, second_session], ignore_index=True)

# Group by Department and Term, sum Reg Count
df_grouped = df_union.groupby(['Department', 'Term'], as_index=False).agg({'Reg Count': 'sum'})

# Pivot to get terms as columns
df_pivot = df_grouped.pivot(index='Department', columns='Term', values='Reg Count')

# Rename columns to string to match target schema
df_pivot.columns = df_pivot.columns.astype(str)

# Ensure all target term columns exist
target_terms = ['20153', '20161', '20162']
for term in target_terms:
    if term not in df_pivot.columns:
        df_pivot[term] = pd.NA

# Select columns in target order
df_result = df_pivot.reset_index()[['Department'] + target_terms]

# Write output
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)