import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_1.csv", index_col=0)

# Join Source1_19_1 (contributions) LEFT JOIN Source1_19_0 (committee info) on calaccess_committee_id
df = pd.merge(df1, df0, on="calaccess_committee_id", how="left", suffixes=('_y', '_x'))

# Rename columns to match target schema exactly (no suffixes)
df = df.rename(columns={
    'ocd_prop_id': 'ocd_prop_id',
    'calaccess_prop_id': 'calaccess_prop_id',
    'ccdc_prop_id': 'ccdc_prop_id',
    'prop_name': 'prop_name',
    'ccdc_committee_id': 'ccdc_committee_id',
    'calaccess_committee_id': 'calaccess_committee_id',
    'committee_name_x': 'committee_name_x',  # from df0 (committee info)
    'committee_position': 'committee_position',
    'committee_name_y': 'committee_name_y',  # from df1 (contributions)
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

# Select columns in target schema order
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

# Convert data types as per target schema
df['calaccess_prop_id'] = pd.to_numeric(df['calaccess_prop_id'], errors='coerce').astype('Int64')
df['ccdc_prop_id'] = pd.to_numeric(df['ccdc_prop_id'], errors='coerce').astype('Int64')
df['ccdc_committee_id'] = pd.to_numeric(df['ccdc_committee_id'], errors='coerce').astype('Int64')
df['calaccess_committee_id'] = pd.to_numeric(df['calaccess_committee_id'], errors='coerce').astype('Int64')
df['calaccess_filing_id'] = pd.to_numeric(df['calaccess_filing_id'], errors='coerce').astype('Int64')
df['contributor_is_self_employed'] = df['contributor_is_self_employed'].astype(bool)
df['amount'] = pd.to_numeric(df['amount'], errors='coerce').astype(float)
df['date_received'] = df['date_received'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_19/target_multisource_mcts.csv", index=False)