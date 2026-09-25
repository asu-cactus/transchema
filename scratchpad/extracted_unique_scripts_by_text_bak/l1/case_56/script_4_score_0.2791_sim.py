import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_56/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={"committee_name": "committee_name_x"})
df_union = pd.concat([df0_renamed, df1], ignore_index=True, sort=False)

df_join = pd.merge(
    df_union,
    df1.rename(columns={"committee_name": "committee_name_y"}),
    on="calaccess_committee_id",
    how="left",
    suffixes=("", "_y")
)

df_join["ocd_prop_id"] = df_join["ocd_prop_id"].astype("string")
df_join["calaccess_prop_id"] = pd.to_numeric(df_join["calaccess_prop_id"], errors="coerce").astype("Int64")
df_join["ccdc_prop_id"] = pd.to_numeric(df_join["ccdc_prop_id"], errors="coerce").astype("Int64")
df_join["prop_name"] = df_join["prop_name"].astype("string")
df_join["ccdc_committee_id"] = pd.to_numeric(df_join["ccdc_committee_id"], errors="coerce").astype("Int64")
df_join["calaccess_committee_id"] = pd.to_numeric(df_join["calaccess_committee_id"], errors="coerce").astype("Int64")
df_join["committee_name_x"] = df_join["committee_name_x"].astype("string")
df_join["committee_position"] = df_join["committee_position"].astype("string")
df_join["committee_name_y"] = df_join["committee_name_y"].astype("string")
df_join["calaccess_filing_id"] = pd.to_numeric(df_join["calaccess_filing_id"], errors="coerce").astype("Int64")
df_join["date_received"] = df_join["date_received"].astype("string")
df_join["contributor_lastname"] = df_join["contributor_lastname"].astype("string")
df_join["contributor_firstname"] = df_join["contributor_firstname"].astype("string")
df_join["contributor_city"] = df_join["contributor_city"].astype("string")
df_join["contributor_state"] = df_join["contributor_state"].astype("string")
df_join["contributor_zip"] = df_join["contributor_zip"].astype("string")
df_join["contributor_employer"] = df_join["contributor_employer"].astype("string")
df_join["contributor_occupation"] = df_join["contributor_occupation"].astype("string")
df_join["contributor_is_self_employed"] = df_join["contributor_is_self_employed"].astype("boolean")
df_join["amount"] = pd.to_numeric(df_join["amount"], errors="coerce").astype(float)

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

df_final = df_join[final_columns]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_56/target_multisource_mcts.csv", index=False)