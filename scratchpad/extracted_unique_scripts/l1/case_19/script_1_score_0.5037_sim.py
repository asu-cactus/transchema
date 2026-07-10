import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="calaccess_committee_id", how="inner", suffixes=('_x', '_y'))

result = merged.rename(columns={
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

result = result[[
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

result['calaccess_prop_id'] = result['calaccess_prop_id'].astype('Int64')
result['ccdc_prop_id'] = result['ccdc_prop_id'].astype('Int64')
result['ccdc_committee_id'] = result['ccdc_committee_id'].astype('Int64')
result['calaccess_committee_id'] = result['calaccess_committee_id'].astype('Int64')
result['calaccess_filing_id'] = result['calaccess_filing_id'].astype('Int64')
result['contributor_is_self_employed'] = result['contributor_is_self_employed'].astype(bool)
result['amount'] = result['amount'].astype(float)
result['date_received'] = result['date_received'].astype(str)
result['ocd_prop_id'] = result['ocd_prop_id'].astype(str)
result['prop_name'] = result['prop_name'].astype(str)
result['committee_name_x'] = result['committee_name_x'].astype(str)
result['committee_position'] = result['committee_position'].astype(str)
result['committee_name_y'] = result['committee_name_y'].astype(str)
result['contributor_lastname'] = result['contributor_lastname'].astype(str)
result['contributor_firstname'] = result['contributor_firstname'].astype(str)
result['contributor_city'] = result['contributor_city'].astype(str)
result['contributor_state'] = result['contributor_state'].astype(str)
result['contributor_zip'] = result['contributor_zip'].astype(str)
result['contributor_employer'] = result['contributor_employer'].astype(str)
result['contributor_occupation'] = result['contributor_occupation'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_19/target_multisource_mcts.csv", index=False)