import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

# Group by PRECINCT and sum numeric columns
df_grouped = df.groupby("PRECINCT", as_index=False).agg({
    "ELIGIBLE_VOTERS": "sum",
    "POLLS": "sum",
    "EARLY_VOING": "sum",
    "ABSENTEE": "sum",
    "PROVISIONAL": "sum"
})

# Convert aggregated columns to int
df_grouped["ELIGIBLE_VOTERS"] = df_grouped["ELIGIBLE_VOTERS"].astype(int)
df_grouped["POLLS"] = df_grouped["POLLS"].astype(int)
df_grouped["EARLY_VOING"] = df_grouped["EARLY_VOING"].astype(int)
df_grouped["ABSENTEE"] = df_grouped["ABSENTEE"].astype(int)
df_grouped["PROVISIONAL"] = df_grouped["PROVISIONAL"].astype(int)

# Reorder columns to match target schema exactly
df_grouped = df_grouped[["PRECINCT", "ELIGIBLE_VOTERS", "POLLS", "EARLY_VOING", "ABSENTEE", "PROVISIONAL"]]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)