import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv", index_col=0)

# Join on user_id
df = pd.merge(df0, df1, on="user_id", how="inner")

# Convert user_id to integer by extracting digits
df["user_id"] = df["user_id"].str.extract(r'(\d+)').astype("Int64")

# Convert time to integer timestamp (seconds since epoch)
df["time"] = pd.to_datetime(df["time"], errors='coerce').view('int64') // 10**9

# Encode email as categorical codes (integer)
df["email"] = df["email"].astype("category").cat.codes.astype("Int64")

# Group by geo, user_id, time, email and aggregate bet and win by sum
df_agg = df.groupby(["geo", "user_id", "time", "email"], dropna=False, as_index=False).agg({
    "bet": "sum",
    "win": "sum"
})

# Reorder columns to match target schema
df_agg = df_agg[["geo", "user_id", "time", "bet", "win", "email"]]

# Write output
df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv", index=False)