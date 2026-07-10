import pandas as pd

# Read source files with index_col=0 to ignore the first index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_1.csv", index_col=0)

# Rename committee_name in df0 to committee_name_x and keep committee_position
df0_renamed = df0.rename(columns={"committee_name": "committee_name_x"})

# Rename committee_name in df1 to committee_name_y
df1_renamed = df1.rename(columns={"committee_name": "committee_name_y"})

# Join on calaccess_committee_id (inner join to keep only matching committees)
merged = pd.merge(
    df0_renamed,
    df1_renamed,
    on="calaccess_committee_id",
    how="inner",
    suffixes=('_x', '_y')
)

# Select and reorder columns to match target schema exactly
result = merged[
    ['ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name', 'ccdc_committee_id',
     'calaccess_committee_id', 'committee_name_x', 'committee_position', 'committee_name_y',
     'calaccess_filing_id', 'date_received', 'contributor_lastname', 'contributor_firstname',
     'contributor_city', 'contributor_state', 'contributor_zip', 'contributor_employer',
     'contributor_occupation', 'contributor_is_self_employed', 'amount']
]

# Cast columns to correct types as per target schema
result['calaccess_prop_id'] = pd.to_numeric(result['calaccess_prop_id'], errors='coerce').astype('Int64')
result['ccdc_prop_id'] = pd.to_numeric(result['ccdc_prop_id'], errors='coerce').astype('Int64')
result['ccdc_committee_id'] = pd.to_numeric(result['ccdc_committee_id'], errors='coerce').astype('Int64')
result['calaccess_committee_id'] = pd.to_numeric(result['calaccess_committee_id'], errors='coerce').astype('Int64')
result['calaccess_filing_id'] = pd.to_numeric(result['calaccess_filing_id'], errors='coerce').astype('Int64')
result['contributor_is_self_employed'] = result['contributor_is_self_employed'].astype('boolean')
result['amount'] = pd.to_numeric(result['amount'], errors='coerce').astype(float)
result['date_received'] = result['date_received'].astype(str)

# Write output to target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_19/target_multisource_mcts.csv", index=False)