import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={
    'committee_name': 'committee_name_x',
})

df1_renamed = df1.rename(columns={
    'committee_name': 'committee_name_y',
})

df_union = pd.concat([df0_renamed, df1_renamed], ignore_index=True, sort=False)

# Add missing columns from target schema if not present
for col in ['ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name', 'ccdc_committee_id', 'committee_position', 'committee_name_x', 'committee_name_y', 'calaccess_filing_id', 'date_received', 'contributor_lastname', 'contributor_firstname', 'contributor_city', 'contributor_state', 'contributor_zip', 'contributor_employer', 'contributor_occupation', 'contributor_is_self_employed', 'amount']:
    if col not in df_union.columns:
        df_union[col] = pd.NA

# Ensure correct dtypes
df_union['ocd_prop_id'] = df_union['ocd_prop_id'].astype("string")
df_union['calaccess_prop_id'] = pd.to_numeric(df_union['calaccess_prop_id'], errors='coerce').astype('Int64')
df_union['ccdc_prop_id'] = pd.to_numeric(df_union['ccdc_prop_id'], errors='coerce').astype('Int64')
df_union['prop_name'] = df_union['prop_name'].astype("string")
df_union['ccdc_committee_id'] = pd.to_numeric(df_union['ccdc_committee_id'], errors='coerce').astype('Int64')
df_union['calaccess_committee_id'] = pd.to_numeric(df_union['calaccess_committee_id'], errors='coerce').astype('Int64')
df_union['committee_name_x'] = df_union['committee_name_x'].astype("string")
df_union['committee_position'] = df_union['committee_position'].astype("string")
df_union['committee_name_y'] = df_union['committee_name_y'].astype("string")
df_union['calaccess_filing_id'] = pd.to_numeric(df_union['calaccess_filing_id'], errors='coerce').astype('Int64')
df_union['date_received'] = df_union['date_received'].astype("string")
df_union['contributor_lastname'] = df_union['contributor_lastname'].astype("string")
df_union['contributor_firstname'] = df_union['contributor_firstname'].astype("string")
df_union['contributor_city'] = df_union['contributor_city'].astype("string")
df_union['contributor_state'] = df_union['contributor_state'].astype("string")
df_union['contributor_zip'] = df_union['contributor_zip'].astype("string")
df_union['contributor_employer'] = df_union['contributor_employer'].astype("string")
df_union['contributor_occupation'] = df_union['contributor_occupation'].astype("string")
df_union['contributor_is_self_employed'] = df_union['contributor_is_self_employed'].astype("boolean")
df_union['amount'] = pd.to_numeric(df_union['amount'], errors='coerce').astype(float)

df_union = df_union[['ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name', 'ccdc_committee_id', 'calaccess_committee_id', 'committee_name_x', 'committee_position', 'committee_name_y', 'calaccess_filing_id', 'date_received', 'contributor_lastname', 'contributor_firstname', 'contributor_city', 'contributor_state', 'contributor_zip', 'contributor_employer', 'contributor_occupation', 'contributor_is_self_employed', 'amount']]

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length1_85/target_multisource_mcts.csv", index=False)