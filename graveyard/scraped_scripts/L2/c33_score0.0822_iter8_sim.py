import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="user_id", how="inner")

df["user_id"] = df["user_id"].str.extract(r'(\d+)').astype(int)
df["email"] = df["email"].str.extract(r'(\d+)').astype(int, errors='ignore')
df["geo"] = df["geo"].astype(str)
df["time"] = pd.to_datetime(df["time"], errors='coerce').dt.day.fillna(0).astype(int)
df["bet"] = pd.to_numeric(df["bet"], errors='coerce').fillna(0).astype(int)
df["win"] = pd.to_numeric(df["win"], errors='coerce').fillna(0).astype(int)

df = df[["geo", "user_id", "time", "bet", "win", "email"]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv", index=False)