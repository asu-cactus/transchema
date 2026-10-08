import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_2/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_2/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_2/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on calaccess_committee_id
merged = pd.merge(df0, df1[['calaccess_committee_id', 'committee_position']], on='calaccess_committee_id', how='inner')

# Group by contributor_firstname, contributor_lastname, committee_position and sum amount
result = merged.groupby(
    ['contributor_firstname', 'contributor_lastname', 'committee_position'], dropna=False, as_index=False
).agg({'amount': 'sum'})

# Write output with exact target schema column names
result.to_csv(target_path, index=False)