import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_85/training_1.csv", index_col=0)

group_cols = [
    "date_received",
    "contributor_city",
    "contributor_state",
    "contributor_zip",
    "contributor_employer",
    "contributor_occupation",
    "contributor_is_self_employed",
]

# The join keys from df1 to group on are:
join_keys = [
    "ocd_prop_id",
    "prop_name",
    "committee_position",
    "committee_name",
]

# Group by the combined keys from df0 and df1 (except aggregations)
group_by_cols = group_cols + join_keys

agg_df0 = df0.groupby(group_cols + ["committee_name"]).agg(
    amount_sum=pd.NamedAgg(column="amount", aggfunc="sum"),
    calaccess_filing_id_count=pd.NamedAgg(column="calaccess_filing_id", aggfunc="count"),
).reset_index()

# We need to join agg_df0 with df1 on committee_name, committee_position, ocd_prop_id, prop_name
# But agg_df0 currently has committee_name but not committee_position, ocd_prop_id, prop_name
# So we must join df0 and df1 first on calaccess_committee_id and committee_name to get those columns before grouping

# Join df0 and df1 on calaccess_committee_id and committee_name to get all needed columns before grouping
df0_1_joined = pd.merge(
    df0,
    df1[["ocd_prop_id", "calaccess_prop_id", "ccdc_prop_id", "prop_name", "ccdc_committee_id", "calaccess_committee_id", "committee_name", "committee_position"]],
    how="left",
    left_on=["calaccess_committee_id", "committee_name"],
    right_on=["calaccess_committee_id", "committee_name"],
)

group_by_cols_full = [
    "date_received",
    "contributor_city",
    "contributor_state",
    "contributor_zip",
    "contributor_employer",
    "contributor_occupation",
    "contributor_is_self_employed",
    "ocd_prop_id",
    "calaccess_prop_id",
    "ccdc_prop_id",
    "prop_name",
    "ccdc_committee_id",
    "calaccess_committee_id",
    "committee_name",
    "committee_position",
]

agg = df0_1_joined.groupby(group_by_cols_full).agg(
    amount=("amount", "sum"),
    calaccess_filing_id=("calaccess_filing_id", "count"),
    contributor_lastname=("contributor_lastname", "first"),
    contributor_firstname=("contributor_firstname", "first"),
).reset_index()

# committee_name_x and committee_name_y are both committee_name from df0 and df1
# We have only one committee_name column after merge, but target schema has committee_name_x and committee_name_y
# So we create committee_name_x from df0's committee_name and committee_name_y from df1's committee_name
# Since we merged on committee_name, they are the same, but to follow target schema, duplicate column

agg["committee_name_x"] = agg["committee_name"]
agg["committee_name_y"] = agg["committee_name"]

# contributor_is_self_employed should be boolean
agg["contributor_is_self_employed"] = agg["contributor_is_self_employed"].astype(bool)

# calaccess_filing_id in target is integer, but we have count, so rename accordingly
agg = agg.rename(columns={"calaccess_filing_id": "calaccess_filing_id"})

# Reorder columns to match target schema
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

result = agg[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_85/target_multisource_mcts.csv", index=False)