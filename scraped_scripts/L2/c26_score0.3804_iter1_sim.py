import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="user_id", how="inner")

df["time"] = pd.to_datetime(df["time"], errors='coerce').dt.hour.fillna(0).astype(int)
df["email"] = df["email"].str.len()
df["geo"] = df["geo"].str.len()
df["bet"] = pd.to_numeric(df["bet"], errors='coerce').fillna(0).astype(int)
df["win"] = pd.to_numeric(df["win"], errors='coerce').fillna(0).astype(int)

result = df[["user_id", "time", "bet", "win", "email", "geo"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv", index=False)