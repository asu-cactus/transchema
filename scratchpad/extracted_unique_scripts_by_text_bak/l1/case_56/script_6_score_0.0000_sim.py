import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_56/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_56/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_56/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(
    df1,
    df0,
    how="inner",
    on=["calaccess_committee_id", "calaccess_filing_id"],
    suffixes=("_x", "_y"),
)

merged = merged.rename(columns={
    "committee_name_x": "committee_name_x",
    "committee_position": "committee_position",
    "committee_name_y": "committee_name_y",
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
})

merged = merged[[
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
]]

merged["calaccess_prop_id"] = pd.to_numeric(merged["calaccess_prop_id"], errors="coerce").astype("Int64")
merged["ccdc_prop_id"] = pd.to_numeric(merged["ccdc_prop_id"], errors="coerce").astype("Int64")
merged["ccdc_committee_id"] = pd.to_numeric(merged["ccdc_committee_id"], errors="coerce").astype("Int64")
merged["calaccess_committee_id"] = pd.to_numeric(merged["calaccess_committee_id"], errors="coerce").astype("Int64")
merged["calaccess_filing_id"] = pd.to_numeric(merged["calaccess_filing_id"], errors="coerce").astype("Int64")
merged["contributor_is_self_employed"] = merged["contributor_is_self_employed"].astype(bool)
merged["amount"] = pd.to_numeric(merged["amount"], errors="coerce").astype(float)

merged.to_csv(target_path, index=False)