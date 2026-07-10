import pandas as pd

# Read source tables with index_col=0
source0_path = "autopipeline-benchmarks/github-pipelines/length1_56/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_56/training_1.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on calaccess_committee_id
df_merged = pd.merge(
    df1,
    df0,
    how='inner',
    on='calaccess_committee_id',
    suffixes=('_x', '_y')
)

# Ensure columns match target schema exactly and types match
# Target schema:
# ['ocd_prop_id': string, 'calaccess_prop_id': integer, 'ccdc_prop_id': integer, 'prop_name': string,
#  'ccdc_committee_id': integer, 'calaccess_committee_id': integer, 'committee_name_x': string,
#  'committee_position': string, 'committee_name_y': string, 'calaccess_filing_id': integer,
#  'date_received': string, 'contributor_lastname': string, 'contributor_firstname': string,
#  'contributor_city': string, 'contributor_state': string, 'contributor_zip': string,
#  'contributor_employer': string, 'contributor_occupation': string,
#  'contributor_is_self_employed': boolean, 'amount': float]

# Select and reorder columns exactly as target schema
final_columns = [
    'ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name',
    'ccdc_committee_id', 'calaccess_committee_id', 'committee_name_x',
    'committee_position', 'committee_name_y', 'calaccess_filing_id',
    'date_received', 'contributor_lastname', 'contributor_firstname',
    'contributor_city', 'contributor_state', 'contributor_zip',
    'contributor_employer', 'contributor_occupation',
    'contributor_is_self_employed', 'amount'
]

df_final = df_merged[final_columns].copy()

# Convert types to match target schema
df_final['calaccess_prop_id'] = df_final['calaccess_prop_id'].astype('Int64')
df_final['ccdc_prop_id'] = df_final['ccdc_prop_id'].astype('Int64')
df_final['ccdc_committee_id'] = df_final['ccdc_committee_id'].astype('Int64')
df_final['calaccess_committee_id'] = df_final['calaccess_committee_id'].astype('Int64')
df_final['calaccess_filing_id'] = df_final['calaccess_filing_id'].astype('Int64')
df_final['contributor_is_self_employed'] = df_final['contributor_is_self_employed'].astype(bool)
df_final['amount'] = df_final['amount'].astype(float)

# Save to target path
output_path = "autopipeline-benchmarks/github-pipelines/length1_56/target_multisource_mcts.csv"
df_final.to_csv(output_path, index=False)