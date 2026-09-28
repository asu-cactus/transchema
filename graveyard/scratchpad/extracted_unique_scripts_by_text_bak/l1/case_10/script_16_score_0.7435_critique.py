import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

agg_df = df.groupby("PRECINCT").agg({
    "ELIGIBLE_VOTERS": "sum",
    "POLLS": "sum",
    "EARLY_VOING": "sum",
    "ABSENTEE": "sum",
    "PROVISIONAL": "sum"
}).reset_index()

agg_df = agg_df[["PRECINCT", "ELIGIBLE_VOTERS", "POLLS", "EARLY_VOING", "ABSENTEE", "PROVISIONAL"]]

for col in ["ELIGIBLE_VOTERS", "POLLS", "EARLY_VOING", "ABSENTEE", "PROVISIONAL"]:
    agg_df[col] = pd.to_numeric(agg_df[col], errors='coerce').fillna(0).astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)