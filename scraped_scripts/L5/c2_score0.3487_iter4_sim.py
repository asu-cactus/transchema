import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

s2_1 = pd.merge(s2, s1, on="zipcode", how="left", suffixes=('_x', '_y'))
s4_1 = pd.merge(s4, s1, on="zipcode", how="left", suffixes=('_x_5', '_y_7'))
s0_1 = pd.merge(s0, s1, on="zipcode", how="left", suffixes=('_x_6', '_y_8'))
s3_1 = pd.merge(s3, s1, on="zipcode", how="left")

# Rename s3_1 columns to match target suffixes for businesses_y and counts_y
s3_1 = s3_1.rename(columns={"businesses": "businesses_y", "counts": "counts_y"})

# Rename s0_1 columns to match target suffixes for businesses_x_5 and counts_x_6
s0_1 = s0_1.rename(columns={"businesses": "businesses_x_5", "counts": "counts_x_6"})

# Rename s4_1 columns to match target suffixes for businesses_y_7 and counts_y_8
s4_1 = s4_1.rename(columns={"businesses": "businesses_y_7", "counts": "counts_y_8"})

# Rename s2_1 columns to match target suffixes for businesses_x and counts_x
s2_1 = s2_1.rename(columns={"businesses": "businesses_x", "counts": "counts_x"})

# s5 has no counts column, rename businesses to businesses and convert to int for counts (0)
s5 = s5.rename(columns={"businesses": "businesses"})
s5["counts"] = 0

# Merge all on zipcode and boro (boro is from s1)
df = s2_1[["zipcode", "businesses_x", "counts_x", "boro"]].copy()
df = df.merge(s3_1[["zipcode", "businesses_y", "counts_y"]], on="zipcode", how="left")
df = df.merge(s4_1[["zipcode", "businesses_y_7", "counts_y_8"]], on="zipcode", how="left")
df = df.merge(s0_1[["zipcode", "businesses_x_5", "counts_x_6"]], on="zipcode", how="left")
df = df.merge(s5[["zipcode", "businesses"]], on="zipcode", how="left")

# Calculate total businesses as sum of counts from s0, s2, s3, s4 plus s5 businesses (which is count of businesses)
# But s5 businesses is count of businesses (integer), others are counts from other sources
# So total businesses = sum of counts_x + counts_y + counts_x_6 + counts_y_8 + businesses (from s5)
df["businesses"] = df["counts_x"].fillna(0).astype(int) + df["counts_y"].fillna(0).astype(int) + df["counts_x_6"].fillna(0).astype(int) + df["counts_y_8"].fillna(0).astype(int) + df["businesses"].fillna(0).astype(int)

df = df[["zipcode", "businesses_x", "counts_x", "businesses_y", "counts_y", "businesses_x_5", "counts_x_6", "businesses_y_7", "counts_y_8", "boro", "businesses"]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv")