import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_1.csv", index_col=0)

df_union = pd.concat([df0, df1[df0.columns.intersection(df1.columns)]], ignore_index=True, sort=False)

df_join = df_union.merge(
    df1,
    on="calaccess_committee_id",
    how="left",
    suffixes=('_x', '_y')
)

result = pd.DataFrame()
result['ocd_prop_id'] = df_join['ocd_prop_id']
result['calaccess_prop_id'] = pd.to_numeric(df_join['calaccess_prop_id'], errors='coerce').astype('Int64')
result['ccdc_prop_id'] = pd.to_numeric(df_join['ccdc_prop_id'], errors='coerce').astype('Int64')
result['prop_name'] = df_join['prop_name']
result['ccdc_committee_id'] = pd.to_numeric(df_join['ccdc_committee_id'], errors='coerce').astype('Int64')
result['calaccess_committee_id'] = pd.to_numeric(df_join['calaccess_committee_id'], errors='coerce').astype('Int64')
result['committee_name_x'] = df_join['committee_name_x']
result['committee_position'] = df_join['committee_position']
result['committee_name_y'] = df_join['committee_name_y']
result['calaccess_filing_id'] = pd.to_numeric(df_join['calaccess_filing_id'], errors='coerce').astype('Int64')
result['date_received'] = df_join['date_received'].astype(str)
result['contributor_lastname'] = df_join['contributor_lastname']
result['contributor_firstname'] = df_join['contributor_firstname']
result['contributor_city'] = df_join['contributor_city']
result['contributor_state'] = df_join['contributor_state']
result['contributor_zip'] = df_join['contributor_zip']
result['contributor_employer'] = df_join['contributor_employer']
result['contributor_occupation'] = df_join['contributor_occupation']
result['contributor_is_self_employed'] = df_join['contributor_is_self_employed'].astype(bool)
result['amount'] = pd.to_numeric(df_join['amount'], errors='coerce').astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_56/target_multisource_mcts.csv", index=False)