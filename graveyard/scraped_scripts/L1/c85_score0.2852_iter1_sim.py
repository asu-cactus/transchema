import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={
    'committee_name': 'committee_name_x'
})

df1_renamed = df1.rename(columns={
    'committee_name': 'committee_name_y'
})

df0_cols = set(df0_renamed.columns)
df1_cols = set(df1_renamed.columns)

common_cols = list(df0_cols.intersection(df1_cols))
# Columns to keep from df0_renamed that are not in df1_renamed (except committee_name_x)
df0_only_cols = [c for c in df0_renamed.columns if c not in common_cols or c == 'committee_name_x']
# Columns to keep from df1_renamed that are not in df0_renamed (except committee_name_y)
df1_only_cols = [c for c in df1_renamed.columns if c not in common_cols or c == 'committee_name_y']

# For union, columns must be the same. We create all columns in both dfs with NaN if missing.
all_columns = set(df0_renamed.columns).union(df1_renamed.columns)

for col in all_columns:
    if col not in df0_renamed.columns:
        df0_renamed[col] = pd.NA
    if col not in df1_renamed.columns:
        df1_renamed[col] = pd.NA

df0_renamed = df0_renamed[sorted(all_columns)]
df1_renamed = df1_renamed[sorted(all_columns)]

df = pd.concat([df0_renamed, df1_renamed], ignore_index=True)

# Add missing columns from target schema with NaN or default values
target_cols = ['ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name', 'ccdc_committee_id',
               'calaccess_committee_id', 'committee_name_x', 'committee_position', 'committee_name_y',
               'calaccess_filing_id', 'date_received', 'contributor_lastname', 'contributor_firstname',
               'contributor_city', 'contributor_state', 'contributor_zip', 'contributor_employer',
               'contributor_occupation', 'contributor_is_self_employed', 'amount']

for col in target_cols:
    if col not in df.columns:
        df[col] = pd.NA

# Reorder columns to target schema order
df = df[target_cols]

# Fix data types according to target schema
df['ocd_prop_id'] = df['ocd_prop_id'].astype('string')
df['calaccess_prop_id'] = pd.to_numeric(df['calaccess_prop_id'], errors='coerce').astype('Int64')
df['ccdc_prop_id'] = pd.to_numeric(df['ccdc_prop_id'], errors='coerce').astype('Int64')
df['prop_name'] = df['prop_name'].astype('string')
df['ccdc_committee_id'] = pd.to_numeric(df['ccdc_committee_id'], errors='coerce').astype('Int64')
df['calaccess_committee_id'] = pd.to_numeric(df['calaccess_committee_id'], errors='coerce').astype('Int64')
df['committee_name_x'] = df['committee_name_x'].astype('string')
df['committee_position'] = df['committee_position'].astype('string')
df['committee_name_y'] = df['committee_name_y'].astype('string')
df['calaccess_filing_id'] = pd.to_numeric(df['calaccess_filing_id'], errors='coerce').astype('Int64')
df['date_received'] = df['date_received'].astype('string')
df['contributor_lastname'] = df['contributor_lastname'].astype('string')
df['contributor_firstname'] = df['contributor_firstname'].astype('string')
df['contributor_city'] = df['contributor_city'].astype('string')
df['contributor_state'] = df['contributor_state'].astype('string')
df['contributor_zip'] = df['contributor_zip'].astype('string')
df['contributor_employer'] = df['contributor_employer'].astype('string')
df['contributor_occupation'] = df['contributor_occupation'].astype('string')
df['contributor_is_self_employed'] = df['contributor_is_self_employed'].astype('boolean')
df['amount'] = pd.to_numeric(df['amount'], errors='coerce').astype('float')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_85/target_multisource_mcts.csv", index=False)