import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on user_id
df = pd.merge(df0, df1, on="user_id", how="inner")

# Convert time to datetime and extract hour as integer
df["time"] = pd.to_datetime(df["time"], errors='coerce').dt.hour

# Encode email and geo as categorical integers
df["email"] = df["email"].astype('category').cat.codes
df["geo"] = df["geo"].astype('category').cat.codes

# Convert bet and win to numeric, fill NaN with 0 and convert to int
df["bet"] = pd.to_numeric(df["bet"], errors='coerce').fillna(0).astype(int)
df["win"] = pd.to_numeric(df["win"], errors='coerce').fillna(0).astype(int)

# Group by user_id and aggregate
# For time: take mode (most frequent hour), if multiple modes, take the smallest
def mode_or_min(series):
    modes = series.mode()
    if len(modes) == 0:
        return pd.NA
    else:
        return modes.min()

agg_df = df.groupby("user_id").agg({
    "time": mode_or_min,
    "bet": "sum",
    "win": "sum",
    "email": "first",
    "geo": "first"
}).reset_index()

# Ensure all columns have correct types
agg_df["time"] = agg_df["time"].astype("Int64")  # nullable integer
agg_df["bet"] = agg_df["bet"].astype(int)
agg_df["win"] = agg_df["win"].astype(int)
agg_df["email"] = agg_df["email"].astype(int)
agg_df["geo"] = agg_df["geo"].astype(int)

# Reorder columns as per target schema
agg_df = agg_df[["user_id", "time", "bet", "win", "email", "geo"]]

agg_df.to_csv(target_path, index=False)