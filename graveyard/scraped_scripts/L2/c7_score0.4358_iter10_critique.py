import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_7/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_7/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_7/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on calaccess_committee_id to use both source tables
df_joined = pd.merge(df0, df1, on='calaccess_committee_id', how='inner')

# Group by contributor_lastname, aggregate contributor_firstname by first occurrence, sum amount
grouped = df_joined.groupby('contributor_lastname', dropna=False, as_index=False).agg({
    'contributor_firstname': 'first',
    'amount': 'sum'
})

# Reorder columns to match target schema
grouped = grouped[['contributor_firstname', 'contributor_lastname', 'amount']]

grouped.to_csv(target_path, index=False)