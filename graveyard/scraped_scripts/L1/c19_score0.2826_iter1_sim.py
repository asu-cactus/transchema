import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_19/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={
    "committee_name": "committee_name_x"
})
df0_renamed["committee_name_y"] = df0_renamed["committee_name_x"]
df0_renamed["calaccess_filing_id"] = pd.NA
df0_renamed["date_received"] = pd.NA
df0_renamed["contributor_lastname"] = pd.NA
df0_renamed["contributor_firstname"] = pd.NA
df0_renamed["contributor_city"] = pd.NA
df0_renamed["contributor_state"] = pd.NA
df0_renamed["contributor_zip"] = pd.NA
df0_renamed["contributor_employer"] = pd.NA
df0_renamed["contributor_occupation"] = pd.NA
df0_renamed["contributor_is_self_employed"] = pd.NA
df0_renamed["amount"] = pd.NA

df1_renamed = df1.rename(columns={
    "committee_name": "committee_name_y"
})
df1_renamed["committee_name_x"] = df1_renamed["committee_name_y"]
df1_renamed["ocd_prop_id"] = pd.NA
df1_renamed["calaccess_prop_id"] = pd.NA
df1_renamed["ccdc_prop_id"] = pd.NA
df1_renamed["prop_name"] = pd.NA
df1_renamed["ccdc_committee_id"] = pd.NA
df1_renamed["committee_position"] = pd.NA

cols = ['ocd_prop_id', 'calaccess_prop_id', 'ccdc_prop_id', 'prop_name', 'ccdc_committee_id', 'calaccess_committee_id',
        'committee_name_x', 'committee_position', 'committee_name_y', 'calaccess_filing_id', 'date_received',
        'contributor_lastname', 'contributor_firstname', 'contributor_city', 'contributor_state', 'contributor_zip',
        'contributor_employer', 'contributor_occupation', 'contributor_is_self_employed', 'amount']

df0_final = df0_renamed[cols]
df1_final = df1_renamed[cols]

df = pd.concat([df0_final, df1_final], ignore_index=True)

df["calaccess_prop_id"] = pd.to_numeric(df["calaccess_prop_id"], errors='coerce').astype("Int64")
df["ccdc_prop_id"] = pd.to_numeric(df["ccdc_prop_id"], errors='coerce').astype("Int64")
df["ccdc_committee_id"] = pd.to_numeric(df["ccdc_committee_id"], errors='coerce').astype("Int64")
df["calaccess_committee_id"] = pd.to_numeric(df["calaccess_committee_id"], errors='coerce').astype("Int64")
df["calaccess_filing_id"] = pd.to_numeric(df["calaccess_filing_id"], errors='coerce').astype("Int64")
df["contributor_is_self_employed"] = df["contributor_is_self_employed"].map({True: True, False: False, 'True': True, 'False': False}).astype("boolean")
df["amount"] = pd.to_numeric(df["amount"], errors='coerce')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_19/target_multisource_mcts.csv", index=False)