import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df = pd.merge(df0, df1, on="user_id", how="inner")

df["time"] = pd.to_datetime(df["time"], errors='coerce').dt.hour
df["email"] = pd.to_numeric(df["email"], errors='coerce')
df["geo"] = pd.to_numeric(df["geo"], errors='coerce')
df["bet"] = pd.to_numeric(df["bet"], errors='coerce').fillna(0).astype(int)
df["win"] = pd.to_numeric(df["win"], errors='coerce').fillna(0).astype(int)

df = df[["user_id", "time", "bet", "win", "email", "geo"]]

df.to_csv(target_path, index=False)