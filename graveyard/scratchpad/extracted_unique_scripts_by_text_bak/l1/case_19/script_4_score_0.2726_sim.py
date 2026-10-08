import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={"committee_name": "committee_name_x"})
df1_renamed = df1.rename(columns={"committee_name": "committee_name_y"})

union_cols = [
    'ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name',
    'ccdc_committee_id', 'calaccess_committee_id', 'committee_name_x', 'committee_position'
]
df0_sel = df0_renamed[union_cols]

# For df1, add missing columns with NaNs to match union_cols except committee_name_x and committee_position
df1_sel = df1_renamed.copy()
for col in union_cols:
    if col not in df1_sel.columns:
        df1_sel[col] = pd.NA
# committee_position does not exist in df1, fill with NaN
if 'committee_position' not in df1_sel.columns:
    df1_sel['committee_position'] = pd.NA
# committee_name_x is from df0, so fill with NaN in df1_sel
df1_sel['committee_name_x'] = pd.NA
df1_sel = df1_sel[union_cols]

union_df = pd.concat([df0_sel, df1_sel], ignore_index=True)

# Now join union_df with df1_renamed on calaccess_committee_id to get the rest of columns from df1
join_cols = [
    'calaccess_filing_id', 'date_received', 'contributor_lastname', 'contributor_firstname',
    'contributor_city', 'contributor_state', 'contributor_zip', 'contributor_employer',
    'contributor_occupation', 'contributor_is_self_employed', 'amount', 'committee_name_y'
]

df1_join_cols = df1_renamed[['calaccess_committee_id'] + join_cols].drop_duplicates(subset=['calaccess_committee_id'])

merged = pd.merge(
    union_df,
    df1_join_cols,
    on='calaccess_committee_id',
    how='left',
    suffixes=('', '_y')
)

# Reorder and cast columns to target schema
result = merged[
    ['ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name', 'ccdc_committee_id',
     'calaccess_committee_id', 'committee_name_x', 'committee_position', 'committee_name_y',
     'calaccess_filing_id', 'date_received', 'contributor_lastname', 'contributor_firstname',
     'contributor_city', 'contributor_state', 'contributor_zip', 'contributor_employer',
     'contributor_occupation', 'contributor_is_self_employed', 'amount']
]

result['calaccess_prop_id'] = pd.to_numeric(result['calaccess_prop_id'], errors='coerce').astype('Int64')
result['ccdc_prop_id'] = pd.to_numeric(result['ccdc_prop_id'], errors='coerce').astype('Int64')
result['ccdc_committee_id'] = pd.to_numeric(result['ccdc_committee_id'], errors='coerce').astype('Int64')
result['calaccess_committee_id'] = pd.to_numeric(result['calaccess_committee_id'], errors='coerce').astype('Int64')
result['calaccess_filing_id'] = pd.to_numeric(result['calaccess_filing_id'], errors='coerce').astype('Int64')
result['contributor_is_self_employed'] = result['contributor_is_self_employed'].astype('boolean')
result['amount'] = pd.to_numeric(result['amount'], errors='coerce').astype(float)
result['date_received'] = result['date_received'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_19/target_multisource_mcts.csv", index=False)