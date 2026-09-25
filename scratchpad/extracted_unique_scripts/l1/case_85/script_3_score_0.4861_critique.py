import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_1.csv", index_col=0)

# Rename committee_name columns before join to preserve both as committee_name_x and committee_name_y
df0_renamed = df0.rename(columns={"committee_name": "committee_name_x"})
df1_renamed = df1.rename(columns={"committee_name": "committee_name_y"})

# Join on calaccess_committee_id and committee_name (df0's committee_name_x and df1's committee_name_y)
# Since we renamed, join keys are:
# df0_renamed.committee_name_x == df1_renamed.committee_name_y
# and calaccess_committee_id matches
joined = pd.merge(
    df0_renamed,
    df1_renamed[
        [
            "ocd_prop_id",
            "calaccess_prop_id",
            "ccdc_prop_id",
            "prop_name",
            "ccdc_committee_id",
            "calaccess_committee_id",
            "committee_name_y",
            "committee_position",
        ]
    ],
    how="inner",
    left_on=["calaccess_committee_id", "committee_name_x"],
    right_on=["calaccess_committee_id", "committee_name_y"],
)

# Define group by columns (leftmost non-float unique keys + contributor info)
group_by_cols = [
    "ocd_prop_id",
    "calaccess_prop_id",
    "ccdc_prop_id",
    "prop_name",
    "ccdc_committee_id",
    "calaccess_committee_id",
    "committee_position",
    "date_received",
    "contributor_lastname",
    "contributor_firstname",
    "contributor_city",
    "contributor_state",
    "contributor_zip",
    "contributor_employer",
    "contributor_occupation",
    "contributor_is_self_employed",
]

# Aggregate amount by sum, calaccess_filing_id by count
agg = (
    joined.groupby(group_by_cols, dropna=False)
    .agg(
        amount=pd.NamedAgg(column="amount", aggfunc="sum"),
        calaccess_filing_id=pd.NamedAgg(column="calaccess_filing_id", aggfunc="count"),
    )
    .reset_index()
)

# Add committee_name_x and committee_name_y columns (already present in group keys or from join)
# committee_name_x and committee_name_y are not in group_by_cols, so add them from joined dataframe
# But committee_name_x and committee_name_y are constant per group, so we can take first()

# Extract committee_name_x and committee_name_y per group by taking first value
committee_names = (
    joined.groupby(group_by_cols, dropna=False)
    .agg(
        committee_name_x=pd.NamedAgg(column="committee_name_x", aggfunc="first"),
        committee_name_y=pd.NamedAgg(column="committee_name_y", aggfunc="first"),
    )
    .reset_index()
)

# Merge committee names back to agg on group_by_cols
result = pd.merge(agg, committee_names, on=group_by_cols, how="left")

# Reorder columns to match target schema exactly
final_cols = [
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

# Ensure contributor_is_self_employed is boolean type
result["contributor_is_self_employed"] = result["contributor_is_self_employed"].astype(bool)

# Ensure calaccess_filing_id is integer type (count)
result["calaccess_filing_id"] = result["calaccess_filing_id"].astype(int)

# Ensure amount is float (sum of amounts)
result["amount"] = result["amount"].astype(float)

# Write to CSV
result[final_cols].to_csv(
    "autopipeline-benchmarks/github-pipelines/length1_85/target_multisource_mcts.csv",
    index=False,
)