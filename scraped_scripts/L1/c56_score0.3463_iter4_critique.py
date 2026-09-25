import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_56/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_56/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_56/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on calaccess_committee_id only
merged = pd.merge(
    df1,
    df0,
    how="inner",
    on=["calaccess_committee_id"],
    suffixes=("_x", "_y"),
)

# Group by the leftmost non-float unique columns in target schema
group_by_cols = [
    "ocd_prop_id",
    "calaccess_prop_id",
    "ccdc_prop_id",
    "prop_name",
    "ccdc_committee_id",
    "calaccess_committee_id",
]

# Aggregations:
# - sum amount (float)
# - for other columns not in group_by, take first (since they are functionally dependent)
agg_dict = {
    "committee_name_x": "first",
    "committee_position": "first",
    "committee_name_y": "first",
    "calaccess_filing_id": "first",
    "date_received": "first",
    "contributor_lastname": "first",
    "contributor_firstname": "first",
    "contributor_city": "first",
    "contributor_state": "first",
    "contributor_zip": "first",
    "contributor_employer": "first",
    "contributor_occupation": "first",
    "contributor_is_self_employed": "first",
    "amount": "sum",
}

grouped = merged.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Cast columns to match target schema types exactly
grouped["calaccess_prop_id"] = grouped["calaccess_prop_id"].astype("Int64")
grouped["ccdc_prop_id"] = grouped["ccdc_prop_id"].astype("Int64")
grouped["ccdc_committee_id"] = grouped["ccdc_committee_id"].astype("Int64")
grouped["calaccess_committee_id"] = grouped["calaccess_committee_id"].astype("Int64")
grouped["calaccess_filing_id"] = grouped["calaccess_filing_id"].astype("Int64")
grouped["date_received"] = grouped["date_received"].astype(str)
grouped["contributor_zip"] = grouped["contributor_zip"].astype(str)
grouped["contributor_is_self_employed"] = grouped["contributor_is_self_employed"].astype(bool)
grouped["amount"] = grouped["amount"].astype(float)

# Reorder columns exactly as target schema
result = grouped[
    [
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
]

result.to_csv(target_path, index=False)