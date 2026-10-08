import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# UNION Source4_47_0 and Source4_47_2 (same schema)
union_0_2 = pd.concat([s0, s2], ignore_index=True)

# JOIN union_0_2 with Source4_47_1 on WarID
join_01 = pd.merge(union_0_2, s1[['WarID', 'IsIntervention']], on="WarID", how="inner")

# JOIN the above with Source4_47_3 on WarID
join_013 = pd.merge(join_01, s3[['WarID', 'IsInternational']], on="WarID", how="inner")

# Select and reorder columns to match target schema
df = join_013[["IsIntervention", "WarID", "WarShortName", "WarType", "IsInternational"]]

# Group by IsIntervention and WarID to remove duplicates if any
df = df.groupby(["IsIntervention", "WarID"], as_index=False).first()

# Ensure correct dtypes as per target schema
df = df.astype({
    "IsIntervention": "Int64",
    "WarID": "Int64",
    "WarShortName": "Int64",
    "WarType": "Int64",
    "IsInternational": "Int64"
})

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)