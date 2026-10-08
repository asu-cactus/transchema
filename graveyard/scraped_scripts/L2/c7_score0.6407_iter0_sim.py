import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_1.csv", index_col=0)

merged = pd.merge(df1, df0[['calaccess_committee_id']], on='calaccess_committee_id', how='inner')

grouped = merged.groupby(['contributor_firstname', 'contributor_lastname'], as_index=False)['amount'].sum()

grouped = grouped.rename(columns={'amount': 'amount', 'contributor_firstname': 'contributor_firstname', 'contributor_lastname': 'contributor_lastname'})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_7/target_multisource_mcts.csv", index=False)