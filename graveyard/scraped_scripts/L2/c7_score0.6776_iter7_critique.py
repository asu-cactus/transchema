import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_1.csv", index_col=0)

# Join on calaccess_committee_id (common key)
joined = pd.merge(df0, df1, on='calaccess_committee_id', how='inner')

# Select only the target columns
result = joined[['contributor_firstname', 'contributor_lastname', 'amount']]

# Ensure correct types as per target schema
result['contributor_firstname'] = result['contributor_firstname'].astype(str)
result['contributor_lastname'] = result['contributor_lastname'].astype(str)
result['amount'] = result['amount'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_7/target_multisource_mcts.csv", index=False)