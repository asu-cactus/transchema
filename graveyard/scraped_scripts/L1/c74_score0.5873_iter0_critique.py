import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_74/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_74/training_1.csv", index_col=0)

# Perform inner join on calaccess_committee_id
merged = pd.merge(df0, df1, on="calaccess_committee_id", how='inner', suffixes=('_x', '_y'))

# Rename columns to match target schema exactly
merged = merged.rename(columns={
    'committee_name_x': 'committee_name_x',
    'committee_position': 'committee_position',
    'committee_name_y': 'committee_name_y',
    'calaccess_filing_id': 'calaccess_filing_id',
    'date_received': 'date_received',
    'contributor_lastname': 'contributor_lastname',
    'contributor_firstname': 'contributor_firstname',
    'contributor_city': 'contributor_city',
    'contributor_state': 'contributor_state',
    'contributor_zip': 'contributor_zip',
    'contributor_employer': 'contributor_employer',
    'contributor_occupation': 'contributor_occupation',
    'contributor_is_self_employed': 'contributor_is_self_employed',
    'amount': 'amount'
})

# Select and reorder columns exactly as target schema
result = merged[[
    'ocd_prop_id',
    'calaccess_prop_id',
    'ccdc_prop_id',
    'prop_name',
    'ccdc_committee_id',
    'calaccess_committee_id',
    'committee_name_x',
    'committee_position',
    'committee_name_y',
    'calaccess_filing_id',
    'date_received',
    'contributor_lastname',
    'contributor_firstname',
    'contributor_city',
    'contributor_state',
    'contributor_zip',
    'contributor_employer',
    'contributor_occupation',
    'contributor_is_self_employed',
    'amount'
]]

# Ensure correct types
result['calaccess_prop_id'] = result['calaccess_prop_id'].astype(int)
result['ccdc_prop_id'] = result['ccdc_prop_id'].astype(int)
result['ccdc_committee_id'] = result['ccdc_committee_id'].astype(int)
result['calaccess_committee_id'] = result['calaccess_committee_id'].astype(int)
result['calaccess_filing_id'] = result['calaccess_filing_id'].astype(int)
result['contributor_is_self_employed'] = result['contributor_is_self_employed'].astype(bool)
result['amount'] = result['amount'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_74/target_multisource_mcts.csv", index=False)