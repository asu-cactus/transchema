import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_4.csv", index_col=0)

agg0 = df0.groupby("batsman", as_index=False).agg(batsman_runs_x=("batsman_runs", "sum"))
agg3 = df3.groupby("batsman", as_index=False).agg(batsman_runs_y=("batsman_runs", "sum"))
agg1 = df1.groupby("batsman", as_index=False).agg(total_runs_x=("total_runs", "sum"))
agg4 = df4.groupby("batsman", as_index=False).agg(total_runs_y=("total_runs", "sum"))

merged = agg1.merge(agg4, on="batsman", how="outer")
merged = merged.merge(agg0, on="batsman", how="outer")
merged = merged.merge(agg3, on="batsman", how="outer")
merged = merged.merge(df2, on="batsman", how="outer")

merged["batsman_runs_x"] = merged["batsman_runs_x"].fillna(0).astype(int)
merged["batsman_runs_y"] = merged["batsman_runs_y"].fillna(0).astype(int)
merged["total_runs_x"] = merged["total_runs_x"].fillna(0).astype(int)
merged["total_runs_y"] = merged["total_runs_y"].fillna(0).astype(int)
merged["no of balls"] = merged["no of balls"].fillna(0).astype(int)
merged["batsman_runs"] = merged["batsman_runs"].fillna(0).astype(int)
merged["strike"] = merged["strike"].astype(float)

merged = merged[["batsman", "total_runs_x", "batsman_runs_x", "batsman_runs_y", "no of balls", "batsman_runs", "strike", "total_runs_y"]]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_34/target_multisource_mcts.csv", index=False)