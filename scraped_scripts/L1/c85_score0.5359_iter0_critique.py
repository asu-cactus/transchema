import pandas as pd

# Read source files with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_1.csv", index_col=0)

# Join on calaccess_committee_id only (inner join)
merged = pd.merge(df1, df0, how="inner", on="calaccess_committee_id", suffixes=('_x', '_y'))

# Rename columns to match target schema exactly
merged = merged.rename(columns={
    'committee_name_x': 'committee_name_x',
    'committee_position': 'committee_position',
    'committee_name_y': 'committee_name_y',
    'ocd_prop_id': 'ocd_prop_id',
    'calaccess_prop_id': 'calaccess_prop_id',
    'ccdc_prop_id': 'ccdc_prop_id',
    'prop_name': 'prop_name',
    'ccdc_committee_id': 'ccdc_committee_id',
    'calaccess_committee_id': 'calaccess_committee_id',
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

# Select columns in the exact order of the target schema
merged = merged[[
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

# Cast columns to correct types as per target schema
merged['calaccess_prop_id'] = pd.to_numeric(merged['calaccess_prop_id'], errors='coerce').astype('Int64')
merged['ccdc_prop_id'] = pd.to_numeric(merged['ccdc_prop_id'], errors='coerce').astype('Int64')
merged['ccdc_committee_id'] = pd.to_numeric(merged['ccdc_committee_id'], errors='coerce').astype('Int64')
merged['calaccess_committee_id'] = pd.to_numeric(merged['calaccess_committee_id'], errors='coerce').astype('Int64')
merged['calaccess_filing_id'] = pd.to_numeric(merged['calaccess_filing_id'], errors='coerce').astype('Int64')
merged['contributor_is_self_employed'] = merged['contributor_is_self_employed'].astype(bool)
merged['amount'] = pd.to_numeric(merged['amount'], errors='coerce').astype(float)

# String columns
str_cols = [
    'date_received', 'ocd_prop_id', 'prop_name', 'committee_name_x', 'committee_position', 'committee_name_y',
    'contributor_lastname', 'contributor_firstname', 'contributor_city', 'contributor_state', 'contributor_zip',
    'contributor_employer', 'contributor_occupation'
]
for col in str_cols:
    merged[col] = merged[col].astype(str)

# Write output CSV without index
merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_85/target_multisource_mcts.csv", index=False)