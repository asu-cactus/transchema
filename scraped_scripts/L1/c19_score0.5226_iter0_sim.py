import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="calaccess_committee_id", how="inner", suffixes=('_x', '_y'))

df = df.rename(columns={
    'committee_name_x': 'committee_name_x',
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

df = df[['ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name', 'ccdc_committee_id', 'calaccess_committee_id',
         'committee_name_x', 'committee_position', 'committee_name_y', 'calaccess_filing_id', 'date_received',
         'contributor_lastname', 'contributor_firstname', 'contributor_city', 'contributor_state', 'contributor_zip',
         'contributor_employer', 'contributor_occupation', 'contributor_is_self_employed', 'amount']]

df['calaccess_prop_id'] = pd.to_numeric(df['calaccess_prop_id'], errors='coerce').astype('Int64')
df['ccdc_prop_id'] = pd.to_numeric(df['ccdc_prop_id'], errors='coerce').astype('Int64')
df['ccdc_committee_id'] = pd.to_numeric(df['ccdc_committee_id'], errors='coerce').astype('Int64')
df['calaccess_committee_id'] = pd.to_numeric(df['calaccess_committee_id'], errors='coerce').astype('Int64')
df['calaccess_filing_id'] = pd.to_numeric(df['calaccess_filing_id'], errors='coerce').astype('Int64')
df['amount'] = pd.to_numeric(df['amount'], errors='coerce').astype(float)
df['contributor_is_self_employed'] = df['contributor_is_self_employed'].astype(bool)
df['date_received'] = df['date_received'].astype(str)
df['prop_name'] = df['prop_name'].astype(str)
df['committee_position'] = df['committee_position'].astype(str)
df['contributor_lastname'] = df['contributor_lastname'].astype(str)
df['contributor_firstname'] = df['contributor_firstname'].astype(str)
df['contributor_city'] = df['contributor_city'].astype(str)
df['contributor_state'] = df['contributor_state'].astype(str)
df['contributor_zip'] = df['contributor_zip'].astype(str)
df['contributor_employer'] = df['contributor_employer'].astype(str)
df['contributor_occupation'] = df['contributor_occupation'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_19/target_multisource_mcts.csv", index=False)