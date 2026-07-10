import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_50/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_50/training_1.csv", index_col=0)

df_merged = pd.merge(df0, df1, on="calaccess_committee_id", suffixes=('_x', '_y'))

df_merged = df_merged.rename(columns={
    'committee_name_x': 'committee_name_x',
    'committee_name_y': 'committee_name_y'
})

df_merged['calaccess_prop_id'] = df_merged['calaccess_prop_id'].astype('Int64')
df_merged['ccdc_prop_id'] = df_merged['ccdc_prop_id'].astype('Int64')
df_merged['ccdc_committee_id'] = df_merged['ccdc_committee_id'].astype('Int64')
df_merged['calaccess_committee_id'] = df_merged['calaccess_committee_id'].astype('Int64')
df_merged['calaccess_filing_id'] = df_merged['calaccess_filing_id'].astype('Int64')
df_merged['amount'] = df_merged['amount'].astype(float)
df_merged['contributor_is_self_employed'] = df_merged['contributor_is_self_employed'].astype(bool)

target_columns = [
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
]

df_target = df_merged[target_columns]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_50/target_multisource_mcts.csv", index=False)