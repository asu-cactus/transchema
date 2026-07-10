import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_1.csv", index_col=0)

# Rename committee_name in df1 to committee_name_y to match target schema
df1_renamed = df1.rename(columns={"committee_name": "committee_name_y"})

# Rename committee_name in df0 to committee_name_x to match target schema
df0_renamed = df0.rename(columns={"committee_name": "committee_name_x"})

# Join on calaccess_committee_id (inner join to keep only matching rows)
df_join = pd.merge(
    df1_renamed,
    df0_renamed,
    on="calaccess_committee_id",
    how="inner",
    suffixes=("", "_drop")  # to avoid duplicate columns if any
)

# Drop any duplicated columns from suffix "_drop" if exist
drop_cols = [col for col in df_join.columns if col.endswith("_drop")]
df_join = df_join.drop(columns=drop_cols)

# Define group by columns (leftmost key columns of target)
group_by_cols = [
    "ocd_prop_id",
    "calaccess_prop_id",
    "ccdc_prop_id",
    "prop_name",
    "ccdc_committee_id",
    "calaccess_committee_id",
]

# Aggregation dictionary:
# sum for amount (float)
# first() for other columns (strings, ints, booleans)
agg_dict = {
    "amount": "sum",
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
}

df_grouped = df_join.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Cast columns to target types exactly

df_grouped["ocd_prop_id"] = df_grouped["ocd_prop_id"].astype("string")
df_grouped["calaccess_prop_id"] = pd.to_numeric(df_grouped["calaccess_prop_id"], errors="coerce").astype("Int64")
df_grouped["ccdc_prop_id"] = pd.to_numeric(df_grouped["ccdc_prop_id"], errors="coerce").astype("Int64")
df_grouped["prop_name"] = df_grouped["prop_name"].astype("string")
df_grouped["ccdc_committee_id"] = pd.to_numeric(df_grouped["ccdc_committee_id"], errors="coerce").astype("Int64")
df_grouped["calaccess_committee_id"] = pd.to_numeric(df_grouped["calaccess_committee_id"], errors="coerce").astype("Int64")
df_grouped["committee_name_x"] = df_grouped["committee_name_x"].astype("string")
df_grouped["committee_position"] = df_grouped["committee_position"].astype("string")
df_grouped["committee_name_y"] = df_grouped["committee_name_y"].astype("string")
df_grouped["calaccess_filing_id"] = pd.to_numeric(df_grouped["calaccess_filing_id"], errors="coerce").astype("Int64")
df_grouped["date_received"] = df_grouped["date_received"].astype("string")
df_grouped["contributor_lastname"] = df_grouped["contributor_lastname"].astype("string")
df_grouped["contributor_firstname"] = df_grouped["contributor_firstname"].astype("string")
df_grouped["contributor_city"] = df_grouped["contributor_city"].astype("string")
df_grouped["contributor_state"] = df_grouped["contributor_state"].astype("string")
df_grouped["contributor_zip"] = df_grouped["contributor_zip"].astype("string")
df_grouped["contributor_employer"] = df_grouped["contributor_employer"].astype("string")
df_grouped["contributor_occupation"] = df_grouped["contributor_occupation"].astype("string")
df_grouped["contributor_is_self_employed"] = df_grouped["contributor_is_self_employed"].astype("boolean")
df_grouped["amount"] = df_grouped["amount"].astype(float)

# Reorder columns exactly as target schema
final_columns = [
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

df_final = df_grouped[final_columns]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_56/target_multisource_mcts.csv", index=False)