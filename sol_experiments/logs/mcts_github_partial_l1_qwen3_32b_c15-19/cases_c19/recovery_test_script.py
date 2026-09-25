import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_19/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_19/test_1.csv', index_col=0)
merged_data = pd.merge(source0, source1, on='calaccess_committee_id')
final_columns = [
    'ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name', 
    'ccdc_committee_id', 'calaccess_committee_id', 'committee_name_x', 
    'committee_position', 'committee_name_y', 'calaccess_filing_id', 
    'date_received', 'contributor_lastname', 'contributor_firstname', 
    'contributor_city', 'contributor_state', 'contributor_zip', 
    'contributor_employer', 'contributor_occupation', 'contributor_is_self_employed', 
    'amount'
]
merged_data[final_columns].to_csv('autopipeline-benchmarks/github-pipelines/length1_19/target_multisource_mcts_recovery_test_val.csv')