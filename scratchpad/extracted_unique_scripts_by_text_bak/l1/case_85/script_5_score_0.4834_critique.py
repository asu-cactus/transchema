import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_1.csv", index_col=0)

# Rename committee_name columns to match target schema
df0 = df0.rename(columns={'committee_name': 'committee_name_x'})
df1 = df1.rename(columns={'committee_name': 'committee_name_y'})

# Join on calaccess_committee_id (integer)
df_joined = pd.merge(df0, df1, how='inner', on='calaccess_committee_id', suffixes=('_x', '_y'))

# Select and reorder columns exactly as target schema
df_joined = df_joined[[
    'ocd_prop_id',          # from df1
    'calaccess_prop_id',    # from df1
    'ccdc_prop_id',         # from df1
    'prop_name',            # from df1
    'ccdc_committee_id',    # from df1
    'calaccess_committee_id', # from both (joined)
    'committee_name_x',     # from df0 (renamed)
    'committee_position',   # from df1
    'committee_name_y',     # from df1 (renamed)
    'calaccess_filing_id',  # from df0
    'date_received',        # from df0
    'contributor_lastname', # from df0
    'contributor_firstname',# from df0
    'contributor_city',     # from df0
    'contributor_state',    # from df0
    'contributor_zip',      # from df0
    'contributor_employer', # from df0
    'contributor_occupation', # from df0
    'contributor_is_self_employed', # from df0
    'amount'                # from df0
]]

# Ensure correct dtypes matching target schema
df_joined['ocd_prop_id'] = df_joined['ocd_prop_id'].astype("string")
df_joined['calaccess_prop_id'] = pd.to_numeric(df_joined['calaccess_prop_id'], errors='coerce').astype('Int64')
df_joined['ccdc_prop_id'] = pd.to_numeric(df_joined['ccdc_prop_id'], errors='coerce').astype('Int64')
df_joined['prop_name'] = df_joined['prop_name'].astype("string")
df_joined['ccdc_committee_id'] = pd.to_numeric(df_joined['ccdc_committee_id'], errors='coerce').astype('Int64')
df_joined['calaccess_committee_id'] = pd.to_numeric(df_joined['calaccess_committee_id'], errors='coerce').astype('Int64')
df_joined['committee_name_x'] = df_joined['committee_name_x'].astype("string")
df_joined['committee_position'] = df_joined['committee_position'].astype("string")
df_joined['committee_name_y'] = df_joined['committee_name_y'].astype("string")
df_joined['calaccess_filing_id'] = pd.to_numeric(df_joined['calaccess_filing_id'], errors='coerce').astype('Int64')
df_joined['date_received'] = df_joined['date_received'].astype("string")
df_joined['contributor_lastname'] = df_joined['contributor_lastname'].astype("string")
df_joined['contributor_firstname'] = df_joined['contributor_firstname'].astype("string")
df_joined['contributor_city'] = df_joined['contributor_city'].astype("string")
df_joined['contributor_state'] = df_joined['contributor_state'].astype("string")
df_joined['contributor_zip'] = df_joined['contributor_zip'].astype("string")
df_joined['contributor_employer'] = df_joined['contributor_employer'].astype("string")
df_joined['contributor_occupation'] = df_joined['contributor_occupation'].astype("string")
df_joined['contributor_is_self_employed'] = df_joined['contributor_is_self_employed'].astype("boolean")
df_joined['amount'] = pd.to_numeric(df_joined['amount'], errors='coerce').astype(float)

# Write output
df_joined.to_csv("autopipeline-benchmarks/github-pipelines/length1_85/target_multisource_mcts.csv", index=False)