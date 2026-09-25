import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_1.csv", index_col=0)

# Join on calaccess_committee_id
df_joined = pd.merge(df0, df1, on='calaccess_committee_id', how='inner')

# Select relevant columns
df_selected = df_joined[['contributor_firstname', 'contributor_lastname', 'amount']]

# Ensure correct types
df_selected['contributor_firstname'] = df_selected['contributor_firstname'].astype(str)
df_selected['contributor_lastname'] = df_selected['contributor_lastname'].astype(str)
df_selected['amount'] = df_selected['amount'].astype(float)

# Group by contributor_firstname and contributor_lastname, sum amount
df_grouped = df_selected.groupby(['contributor_firstname', 'contributor_lastname'], as_index=False).agg({'amount': 'sum'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_7/target_multisource_mcts.csv", index=False)