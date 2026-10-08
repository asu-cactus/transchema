import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_1.csv", index_col=0)

group_cols = [
    "date_received",
    "contributor_city",
    "contributor_state",
    "contributor_zip",
    "contributor_employer",
    "contributor_occupation",
    "contributor_is_self_employed",
    "committee_name",
]

# We need to join on committee_name, committee_position, ocd_prop_id, prop_name from df1
# But df0 does not have ocd_prop_id, prop_name, committee_position, so we first join df0 and df1 on committee_name
# However, the partial plan groups by columns including ocd_prop_id, prop_name, committee_position from df1
# So first join df0 and df1 on committee_name to get those columns, then group by all required columns

# Merge df0 and df1 on committee_name to get ocd_prop_id, prop_name, committee_position
df_merged = pd.merge(
    df0,
    df1[
        [
            "ocd_prop_id",
            "calaccess_prop_id",
            "ccdc_prop_id",
            "prop_name",
            "ccdc_committee_id",
            "calaccess_committee_id",
            "committee_name",
            "committee_position",
        ]
    ],
    on="committee_name",
    how="inner",
    suffixes=("_0", "_1"),
)

group_by_cols = [
    "date_received",
    "contributor_city",
    "contributor_state",
    "contributor_zip",
    "contributor_employer",
    "contributor_occupation",
    "contributor_is_self_employed",
    "ocd_prop_id",
    "prop_name",
    "committee_position",
    "committee_name",
]

agg_df = (
    df_merged.groupby(group_by_cols)
    .agg(
        amount=pd.NamedAgg(column="amount", aggfunc="sum"),
        calaccess_filing_id=pd.NamedAgg(column="calaccess_filing_id", aggfunc="count"),
    )
    .reset_index()
)

# Now join agg_df back to df1 to get the remaining columns: calaccess_prop_id, ccdc_prop_id, ccdc_committee_id, calaccess_committee_id, committee_name_y (from df1.committee_name), calaccess_filing_id (integer), contributor_lastname, contributor_firstname

# contributor_lastname and contributor_firstname are missing in agg_df because they were not grouped by or aggregated
# They exist in df0, so we need to join agg_df back to df0 on all group by columns except the ones from df1 (ocd_prop_id, prop_name, committee_position)
# But contributor_lastname and contributor_firstname are not in group_by_cols, so we cannot get them by groupby aggregation
# So we must include contributor_lastname and contributor_firstname in groupby to preserve them (or use a different approach)

# The target schema requires contributor_lastname and contributor_firstname at row level, so grouping by them is necessary

# So redo groupby including contributor_lastname and contributor_firstname

group_by_cols_full = group_by_cols + ["contributor_lastname", "contributor_firstname"]

agg_df_full = (
    df_merged.groupby(group_by_cols_full)
    .agg(
        amount=pd.NamedAgg(column="amount", aggfunc="sum"),
        calaccess_filing_id=pd.NamedAgg(column="calaccess_filing_id", aggfunc="count"),
    )
    .reset_index()
)

# Now join agg_df_full with df1 on committee_name, committee_position, ocd_prop_id, prop_name to get calaccess_prop_id, ccdc_prop_id, ccdc_committee_id, calaccess_committee_id, committee_name_y

df_final = pd.merge(
    agg_df_full,
    df1[
        [
            "ocd_prop_id",
            "calaccess_prop_id",
            "ccdc_prop_id",
            "prop_name",
            "ccdc_committee_id",
            "calaccess_committee_id",
            "committee_name",
            "committee_position",
        ]
    ].drop_duplicates(),
    on=["ocd_prop_id", "prop_name", "committee_position", "committee_name"],
    how="left",
    suffixes=("", "_y"),
)

# Rename columns to match target schema
df_final = df_final.rename(
    columns={
        "committee_name": "committee_name_x",
        "committee_name_y": "committee_name_y",
        "calaccess_filing_id": "calaccess_filing_id",
    }
)

# Add missing columns from target schema with NaN or appropriate types
for col, dtype in {
    "calaccess_prop_id": "Int64",
    "ccdc_prop_id": "Int64",
    "ccdc_committee_id": "Int64",
    "calaccess_committee_id": "Int64",
    "committee_name_y": "string",
    "calaccess_filing_id": "Int64",
    "contributor_is_self_employed": "boolean",
    "amount": "float",
}.items():
    if col not in df_final.columns:
        df_final[col] = pd.NA
    df_final[col] = df_final[col].astype(dtype)

# Ensure contributor_is_self_employed is boolean
df_final["contributor_is_self_employed"] = df_final["contributor_is_self_employed"].astype("boolean")

# Reorder columns to target schema order
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

df_final = df_final[target_columns]

df_final.to_csv(
    "autopipeline-benchmarks/github-pipelines/length1_56/target_multisource_mcts.csv",
    index=False,
)