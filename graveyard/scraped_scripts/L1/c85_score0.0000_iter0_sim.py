import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, how="inner", on=["calaccess_committee_id", "calaccess_filing_id"], suffixes=('_x', '_y'))

merged = merged.rename(columns={
    'committee_name_x': 'committee_name_x',
    'committee_name_y': 'committee_name_y',
    'ocd_prop_id': 'ocd_prop_id',
    'calaccess_prop_id': 'calaccess_prop_id',
    'ccdc_prop_id': 'ccdc_prop_id',
    'prop_name': 'prop_name',
    'ccdc_committee_id': 'ccdc_committee_id',
    'calaccess_committee_id': 'calaccess_committee_id',
    'committee_position': 'committee_position',
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

merged['calaccess_prop_id'] = pd.to_numeric(merged['calaccess_prop_id'], errors='coerce').astype('Int64')
merged['ccdc_prop_id'] = pd.to_numeric(merged['ccdc_prop_id'], errors='coerce').astype('Int64')
merged['ccdc_committee_id'] = pd.to_numeric(merged['ccdc_committee_id'], errors='coerce').astype('Int64')
merged['calaccess_committee_id'] = pd.to_numeric(merged['calaccess_committee_id'], errors='coerce').astype('Int64')
merged['calaccess_filing_id'] = pd.to_numeric(merged['calaccess_filing_id'], errors='coerce').astype('Int64')
merged['contributor_is_self_employed'] = merged['contributor_is_self_employed'].astype(bool)
merged['amount'] = pd.to_numeric(merged['amount'], errors='coerce').astype(float)
merged['date_received'] = merged['date_received'].astype(str)
merged['ocd_prop_id'] = merged['ocd_prop_id'].astype(str)
merged['prop_name'] = merged['prop_name'].astype(str)
merged['committee_name_x'] = merged['committee_name_x'].astype(str)
merged['committee_position'] = merged['committee_position'].astype(str)
merged['committee_name_y'] = merged['committee_name_y'].astype(str)
merged['contributor_lastname'] = merged['contributor_lastname'].astype(str)
merged['contributor_firstname'] = merged['contributor_firstname'].astype(str)
merged['contributor_city'] = merged['contributor_city'].astype(str)
merged['contributor_state'] = merged['contributor_state'].astype(str)
merged['contributor_zip'] = merged['contributor_zip'].astype(str)
merged['contributor_employer'] = merged['contributor_employer'].astype(str)
merged['contributor_occupation'] = merged['contributor_occupation'].astype(str)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_85/target_multisource_mcts.csv", index=False)