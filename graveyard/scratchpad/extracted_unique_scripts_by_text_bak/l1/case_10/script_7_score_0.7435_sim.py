import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

# The partial plan suggests a self-join on LEGISLATIVE_DISTRICT_CODE and PRECINCT, but joining the same table on itself with identical keys and no suffixes or different columns is redundant.
# Instead, we aggregate directly by PRECINCT summing the relevant columns.

df_grouped = df0.groupby("PRECINCT", as_index=False).agg({
    "ELIGIBLE_VOTERS": "sum",
    "POLLS": "sum",
    "EARLY_VOING": "sum",
    "ABSENTEE": "sum",
    "PROVISIONAL": "sum"
})

# Ensure correct dtypes
df_grouped["PRECINCT"] = df_grouped["PRECINCT"].astype(str)
df_grouped["ELIGIBLE_VOTERS"] = df_grouped["ELIGIBLE_VOTERS"].astype(int)
df_grouped["POLLS"] = df_grouped["POLLS"].astype(int)
df_grouped["EARLY_VOING"] = df_grouped["EARLY_VOING"].astype(int)
df_grouped["ABSENTEE"] = df_grouped["ABSENTEE"].astype(int)
df_grouped["PROVISIONAL"] = df_grouped["PROVISIONAL"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)