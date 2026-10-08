import pandas as pd

# Read source tables with index_col=0 to ignore the first numerical index column
source0_path = "autopipeline-benchmarks/github-pipelines/length1_85/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_85/training_1.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on calaccess_committee_id (integer)
# Use inner join to keep only matching rows
df_merged = pd.merge(
    df1,
    df0,
    how="inner",
    on="calaccess_committee_id",
    suffixes=("_x", "_y")
)

# Reorder columns to match target schema exactly
target_columns = [
    'ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name', 'ccdc_committee_id',
    'calaccess_committee_id', 'committee_name_x', 'committee_position', 'committee_name_y',
    'calaccess_filing_id', 'date_received', 'contributor_lastname', 'contributor_firstname',
    'contributor_city', 'contributor_state', 'contributor_zip', 'contributor_employer',
    'contributor_occupation', 'contributor_is_self_employed', 'amount'
]

# The join will produce committee_name_x and committee_name_y columns from suffixes
# Ensure all columns exist, if not, create with NaN (should not happen here)
for col in target_columns:
    if col not in df_merged.columns:
        df_merged[col] = pd.NA

df_final = df_merged[target_columns]

# Write to target CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_85/target_multisource_mcts.csv", index=False)