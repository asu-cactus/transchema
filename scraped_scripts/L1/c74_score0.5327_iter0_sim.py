import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_74/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_74/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="calaccess_committee_id", suffixes=('_x', '_y'))

result = pd.DataFrame()
result['ocd_prop_id'] = merged['ocd_prop_id']
result['calaccess_prop_id'] = merged['calaccess_prop_id']
result['ccdc_prop_id'] = merged['ccdc_prop_id']
result['prop_name'] = merged['prop_name']
result['ccdc_committee_id'] = merged['ccdc_committee_id']
result['calaccess_committee_id'] = merged['calaccess_committee_id']
result['committee_name_x'] = merged['committee_name_x']
result['committee_position'] = merged['committee_position']
result['committee_name_y'] = merged['committee_name_y']
result['calaccess_filing_id'] = merged['calaccess_filing_id']
result['date_received'] = merged['date_received']
result['contributor_lastname'] = merged['contributor_lastname']
result['contributor_firstname'] = merged['contributor_firstname']
result['contributor_city'] = merged['contributor_city']
result['contributor_state'] = merged['contributor_state']
result['contributor_zip'] = merged['contributor_zip']
result['contributor_employer'] = merged['contributor_employer']
result['contributor_occupation'] = merged['contributor_occupation']
result['contributor_is_self_employed'] = merged['contributor_is_self_employed'].astype(bool)
result['amount'] = merged['amount'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_74/target_multisource_mcts.csv", index=False)