import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="calaccess_committee_id")

group_cols = [
    "committee_position",
    "committee_name",
    "date_received",
    "contributor_city",
    "contributor_state",
    "contributor_zip",
    "contributor_employer",
    "contributor_occupation",
    "contributor_is_self_employed",
    "ocd_prop_id",
    "prop_name"
]

agg_dict = {
    "contributor_firstname": "min",
    "contributor_lastname": "min",
    "amount": "sum"
}

grouped = merged.groupby(group_cols).agg(agg_dict).reset_index()

result = grouped[["contributor_firstname", "contributor_lastname", "amount"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_7/target_multisource_mcts.csv", index=False)