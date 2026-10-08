import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_3.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)
union_df = union_df.rename(columns={"total_runs": "total_runs", "batsman": "batsman"})

join1 = pd.merge(union_df, df2, on="batsman", how="inner")
join1 = join1.rename(columns={"batsman_runs": "batsman_runs_x"})

join2 = pd.merge(join1, df3, on="batsman", how="inner")
join2 = join2.rename(columns={"batsman_runs": "batsman_runs_y"})

grouped = join2.groupby("batsman").agg(
    batsman_runs_x=("batsman_runs_x", "mean"),
    total_runs=("total_runs", "sum"),
    batsman_runs_y=("batsman_runs_y", "mean"),
    batsman_runs=("batsman_runs_y", "sum"),
).reset_index()

grouped["batsman_runs"] = 0

grouped = grouped.astype({
    "batsman": str,
    "batsman_runs_x": float,
    "total_runs": int,
    "batsman_runs_y": float,
    "batsman_runs": int,
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_38/target_multisource_mcts.csv", index=False)