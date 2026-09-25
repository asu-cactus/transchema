import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_1.csv", index_col=0)

# Join on calaccess_committee_id
df_merged = pd.merge(
    df0,
    df1,
    on="calaccess_committee_id",
    how="inner",
    suffixes=("_x", "_y"),
)

# Rename columns to match target schema exactly
df_merged = df_merged.rename(
    columns={
        "committee_name_x": "committee_name_x",  # from df0.committee_name
        "committee_name_y": "committee_name_y",  # from df1.committee_name
        "committee_position": "committee_position",
        "ocd_prop_id": "ocd_prop_id",
        "calaccess_prop_id": "calaccess_prop_id",
        "ccdc_prop_id": "ccdc_prop_id",
        "prop_name": "prop_name",
        "ccdc_committee_id": "ccdc_committee_id",
        "calaccess_committee_id": "calaccess_committee_id",
        "calaccess_filing_id": "calaccess_filing_id",
        "date_received": "date_received",
        "contributor_lastname": "contributor_lastname",
        "contributor_firstname": "contributor_firstname",
        "contributor_city": "contributor_city",
        "contributor_state": "contributor_state",
        "contributor_zip": "contributor_zip",
        "contributor_employer": "contributor_employer",
        "contributor_occupation": "contributor_occupation",
        "contributor_is_self_employed": "contributor_is_self_employed",
        "amount": "amount",
    }
)

# Select columns in target schema order
target_columns = [
    "ocd_prop_id",
    "calaccess_prop_id",
    "ccdc_prop_id",
    "prop_name",
    "ccdc_committee_id",
    "calaccess_committee_id",
    "committee_name_x",
    "committee_position",
    "committee_name_y",
    "calaccess_filing_id",
    "date_received",
    "contributor_lastname",
    "contributor_firstname",
    "contributor_city",
    "contributor_state",
    "contributor_zip",
    "contributor_employer",
    "contributor_occupation",
    "contributor_is_self_employed",
    "amount",
]

df_final = df_merged[target_columns]

# Ensure correct dtypes
df_final["calaccess_prop_id"] = pd.to_numeric(df_final["calaccess_prop_id"], errors="coerce").astype("Int64")
df_final["ccdc_prop_id"] = pd.to_numeric(df_final["ccdc_prop_id"], errors="coerce").astype("Int64")
df_final["ccdc_committee_id"] = pd.to_numeric(df_final["ccdc_committee_id"], errors="coerce").astype("Int64")
df_final["calaccess_committee_id"] = pd.to_numeric(df_final["calaccess_committee_id"], errors="coerce").astype("Int64")
df_final["calaccess_filing_id"] = pd.to_numeric(df_final["calaccess_filing_id"], errors="coerce").astype("Int64")
df_final["contributor_is_self_employed"] = df_final["contributor_is_self_employed"].astype("boolean")
df_final["amount"] = pd.to_numeric(df_final["amount"], errors="coerce").astype(float)

# Write output
df_final.to_csv(
    "autopipeline-benchmarks/github-pipelines/length1_56/target_multisource_mcts.csv",
    index=False,
)