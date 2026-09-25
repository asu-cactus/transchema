import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_0.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_3.csv", index_col=0)

join_0_2 = pd.merge(s0, s2, on="batsman", how="inner", suffixes=('_x', '_y'))
join_all = pd.merge(join_0_2, s3, on="batsman", how="inner", suffixes=('_x', '_y'))

grouped = join_all.groupby("batsman", as_index=False).agg({
    "total_runs": "sum",
    "batsman_runs_x": "sum",
    "batsman_runs_y": "sum"
})

grouped["batsman_runs"] = 0
grouped["total_runs"] = grouped["total_runs"].astype(int)
grouped["batsman_runs"] = grouped["batsman_runs"].astype(int)

grouped = grouped[["batsman", "batsman_runs_x", "total_runs", "batsman_runs_y", "batsman_runs"]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_38/target_multisource_mcts.csv", index=False)