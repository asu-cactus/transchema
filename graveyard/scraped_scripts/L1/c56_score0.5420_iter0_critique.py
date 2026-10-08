import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_1.csv", index_col=0)

# Join on calaccess_committee_id only
merged = pd.merge(df1, df0, how="inner", on="calaccess_committee_id", suffixes=('_x', '_y'))

# Cast columns to match target schema types
merged['calaccess_prop_id'] = merged['calaccess_prop_id'].astype('Int64')
merged['ccdc_prop_id'] = merged['ccdc_prop_id'].astype('Int64')
merged['ccdc_committee_id'] = merged['ccdc_committee_id'].astype('Int64')
merged['calaccess_committee_id'] = merged['calaccess_committee_id'].astype('Int64')
merged['calaccess_filing_id'] = merged['calaccess_filing_id'].astype('Int64')
merged['contributor_is_self_employed'] = merged['contributor_is_self_employed'].astype(bool)
merged['amount'] = merged['amount'].astype(float)

# Select columns in the exact order and names as target schema
result = merged[['ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name', 'ccdc_committee_id', 'calaccess_committee_id',
                 'committee_name_x', 'committee_position', 'committee_name_y', 'calaccess_filing_id', 'date_received',
                 'contributor_lastname', 'contributor_firstname', 'contributor_city', 'contributor_state', 'contributor_zip',
                 'contributor_employer', 'contributor_occupation', 'contributor_is_self_employed', 'amount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_56/target_multisource_mcts.csv", index=False)