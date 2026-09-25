import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

agg_df = df.groupby("PRECINCT").agg({
    "PARTY": "count",
    "ELIGIBLE_VOTERS": "max",
    "POLLS": "max",
    "EARLY_VOING": "max",
    "ABSENTEE": "max",
    "PROVISIONAL": "max"
}).reset_index()

agg_df = agg_df.rename(columns={
    "PARTY": "COUNT_PARTY",
    "ELIGIBLE_VOTERS": "ELIGIBLE_VOTERS",
    "POLLS": "POLLS",
    "EARLY_VOING": "EARLY_VOING",
    "ABSENTEE": "ABSENTEE",
    "PROVISIONAL": "PROVISIONAL"
})

agg_df = agg_df[["PRECINCT", "ELIGIBLE_VOTERS", "POLLS", "EARLY_VOING", "ABSENTEE", "PROVISIONAL"]]

for col in ["ELIGIBLE_VOTERS", "POLLS", "EARLY_VOING", "ABSENTEE", "PROVISIONAL"]:
    agg_df[col] = pd.to_numeric(agg_df[col], errors='coerce').fillna(0).astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)