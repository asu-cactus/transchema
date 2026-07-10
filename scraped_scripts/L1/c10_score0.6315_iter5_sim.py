import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

agg_df = df.groupby("PRECINCT", as_index=False).agg({
    "ELIGIBLE_VOTERS": "mean",
    "POLLS": "mean",
    "EARLY_VOING": "mean",
    "ABSENTEE": "mean",
    "PROVISIONAL": "mean"
})

agg_df["ELIGIBLE_VOTERS"] = agg_df["ELIGIBLE_VOTERS"].round().astype("Int64")
agg_df["POLLS"] = agg_df["POLLS"].round().astype("Int64")
agg_df["EARLY_VOING"] = agg_df["EARLY_VOING"].round().astype("Int64")
agg_df["ABSENTEE"] = agg_df["ABSENTEE"].round().astype("Int64")
agg_df["PROVISIONAL"] = agg_df["PROVISIONAL"].round().astype("Int64")

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)