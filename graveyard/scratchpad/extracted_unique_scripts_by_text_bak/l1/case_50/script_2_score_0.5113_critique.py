import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_50/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_50/training_1.csv", index_col=0)

# Join on calaccess_committee_id
df = pd.merge(df0, df1, on="calaccess_committee_id", how="inner", suffixes=('_x', '_y'))

# Select and reorder columns exactly as in target schema
df = df[[
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
df['calaccess_prop_id'] = df['calaccess_prop_id'].astype('Int64')
df['ccdc_prop_id'] = df['ccdc_prop_id'].astype('Int64')
df['ccdc_committee_id'] = df['ccdc_committee_id'].astype('Int64')
df['calaccess_committee_id'] = df['calaccess_committee_id'].astype('Int64')
df['calaccess_filing_id'] = df['calaccess_filing_id'].astype('Int64')
df['contributor_is_self_employed'] = df['contributor_is_self_employed'].astype(bool)
df['amount'] = df['amount'].astype(float)
df['date_received'] = df['date_received'].astype(str)
df['ocd_prop_id'] = df['ocd_prop_id'].astype(str)
df['prop_name'] = df['prop_name'].astype(str)
df['committee_name_x'] = df['committee_name_x'].astype(str)
df['committee_position'] = df['committee_position'].astype(str)
df['committee_name_y'] = df['committee_name_y'].astype(str)
df['contributor_lastname'] = df['contributor_lastname'].astype(str)
df['contributor_firstname'] = df['contributor_firstname'].astype(str)
df['contributor_city'] = df['contributor_city'].astype(str)
df['contributor_state'] = df['contributor_state'].astype(str)
df['contributor_zip'] = df['contributor_zip'].astype(str)
df['contributor_employer'] = df['contributor_employer'].astype(str)
df['contributor_occupation'] = df['contributor_occupation'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_50/target_multisource_mcts.csv", index=False)