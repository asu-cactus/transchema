import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

# Rename businesses and counts columns in each source to match target schema columns

# s4 -> businesses_x, counts_x (Sidewalk Cafe)
s4_renamed = s4.rename(columns={"businesses": "businesses_x", "counts": "counts_x"})

# s2 -> businesses_y, counts_y (Pawnbroker)
s2_renamed = s2.rename(columns={"businesses": "businesses_y", "counts": "counts_y"})

# s0 -> businesses_x_5, counts_x_6 (Debt Collection Agency)
# s0 has businesses string, counts int, but target expects businesses_x_5 string and counts_x_6 int
# However, s5 is the source with only zipcode and businesses (int), no business name string.
# The target examples show "Debt Collection Agency" as businesses_x_5, counts_x_6 is from s0 counts.
# So s0 is Debt Collection Agency with counts, s5 is the integer count of businesses (businesses column) for Debt Collection Agency.
# So rename s0 businesses to businesses_x_5, counts to counts_x_6
s0_renamed = s0.rename(columns={"businesses": "businesses_x_5", "counts": "counts_x_6"})

# s3 -> businesses_y_7, counts_y_8 (Cigarette Retail Dealer)
s3_renamed = s3.rename(columns={"businesses": "businesses_y_7", "counts": "counts_y_8"})

# s5 -> businesses (int count), no business name string
# We will add a constant business name "Debt Collection Agency" for this source
# Rename s5 businesses column to "businesses" (int)
s5_renamed = s5.rename(columns={"businesses": "businesses"})

# Join s4 and s2 on zipcode
df = pd.merge(s4_renamed, s2_renamed, on="zipcode", how="inner")

# Join with s0 on zipcode
df = pd.merge(df, s0_renamed, on="zipcode", how="inner")

# Join with s3 on zipcode
df = pd.merge(df, s3_renamed, on="zipcode", how="inner")

# Join with s5 on zipcode
df = pd.merge(df, s5_renamed, on="zipcode", how="inner")

# Add the constant business name "Debt Collection Agency" for businesses_x_5 column
# But s0 already has businesses_x_5 column from s0.businesses, which is string "Debt Collection Agency" per source info
# However, s0 businesses column contains the business name string, so no need to overwrite
# But s5 has no business name string, so we do not overwrite businesses_x_5 from s0
# The target schema has businesses_x_5 as string "Debt Collection Agency" (from s0), counts_x_6 as counts from s0
# The businesses column (last column) is from s5.businesses (int count)
# So no overwrite needed here

# Join with s1 (boro) on zipcode
df = pd.merge(df, s1, on="zipcode", how="inner")

# Ensure correct dtypes
df["zipcode"] = df["zipcode"].astype(int)

for col in ["counts_x", "counts_y", "counts_x_6", "counts_y_8", "businesses"]:
    df[col] = df[col].fillna(0).astype(int)

for col in ["businesses_x", "businesses_y", "businesses_x_5", "businesses_y_7", "boro"]:
    df[col] = df[col].fillna("").astype(str)

# Reorder columns to target schema
df = df[[
    "zipcode",
    "businesses_x",
    "counts_x",
    "businesses_y",
    "counts_y",
    "businesses_x_5",
    "counts_x_6",
    "businesses_y_7",
    "counts_y_8",
    "boro",
    "businesses"
]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv", index=False)