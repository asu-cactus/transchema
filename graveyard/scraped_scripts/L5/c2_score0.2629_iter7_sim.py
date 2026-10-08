import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

agg0 = s0.groupby("zipcode", as_index=False)["counts"].sum().rename(columns={"counts": "counts_0"})
agg2 = s2.groupby("zipcode", as_index=False)["counts"].sum().rename(columns={"counts": "counts_2"})
agg3 = s3.groupby("zipcode", as_index=False)["counts"].sum().rename(columns={"counts": "counts_3"})
agg4 = s4.groupby("zipcode", as_index=False)["counts"].sum().rename(columns={"counts": "counts_4"})
agg5 = s5.groupby("zipcode", as_index=False)["businesses"].sum().rename(columns={"businesses": "businesses_5"})

df = agg0.merge(agg2, on="zipcode", how="outer")
df = df.merge(agg3, on="zipcode", how="outer")
df = df.merge(agg4, on="zipcode", how="outer")
df = df.merge(agg5, on="zipcode", how="outer")

# Now join back to original source tables to get business names for each counts/businesses column
# We want to get the business names corresponding to each counts/businesses column in the target schema:
# businesses_x, counts_x from Source5_2_4 (Sidewalk Cafe)
# businesses_y, counts_y from Source5_2_2 (Pawnbroker)
# businesses_x_5, counts_x_6 from Source5_2_5 (Debt Collection Agency) - but s5 has no counts, only businesses (sum done)
# businesses_y_7, counts_y_8 from Source5_2_3 (Cigarette Retail Dealer)
# boro from Source5_2_1
# businesses from Source5_2_5 (sum of businesses)

# For each source with businesses and counts, get the business name per zipcode by taking the most frequent business or the first business (since examples show one business per zipcode per source)
# Because the target schema has string columns for businesses_x, businesses_y, businesses_x_5, businesses_y_7, we need to get the business names from the source tables.

# Extract business names per zipcode from s4 (Sidewalk Cafe)
b_x = s4.groupby("zipcode", as_index=False).agg({"businesses": lambda x: x.mode().iat[0] if not x.mode().empty else x.iloc[0]})
b_x = b_x.rename(columns={"businesses": "businesses_x"})

# Extract business names per zipcode from s2 (Pawnbroker)
b_y = s2.groupby("zipcode", as_index=False).agg({"businesses": lambda x: x.mode().iat[0] if not x.mode().empty else x.iloc[0]})
b_y = b_y.rename(columns={"businesses": "businesses_y"})

# Extract business names per zipcode from s5 (Debt Collection Agency) - s5 has no counts, only businesses (integers)
# But target has businesses_x_5 (string) and counts_x_6 (integer)
# The counts_x_6 corresponds to counts from s5? No counts in s5, so counts_x_6 is sum of businesses in s5 (already agg5)
# For businesses_x_5, we need a string business name. The example shows "Debt Collection Agency" for businesses_x_5.
# Since s5 has no businesses string column, only integer businesses count, we must hardcode the business name "Debt Collection Agency" for all rows.
# This is consistent with the example and the source info.

b_x_5 = pd.DataFrame({"zipcode": agg5["zipcode"], "businesses_x_5": "Debt Collection Agency"})

# Extract business names per zipcode from s3 (Cigarette Retail Dealer)
b_y_7 = s3.groupby("zipcode", as_index=False).agg({"businesses": lambda x: x.mode().iat[0] if not x.mode().empty else x.iloc[0]})
b_y_7 = b_y_7.rename(columns={"businesses": "businesses_y_7"})

# Join all business names to df
df = df.merge(b_x, on="zipcode", how="left")
df = df.merge(b_y, on="zipcode", how="left")
df = df.merge(b_x_5, on="zipcode", how="left")
df = df.merge(b_y_7, on="zipcode", how="left")

# Join boro from s1
df = df.merge(s1, on="zipcode", how="left")

# Rename aggregated columns to match target schema
df = df.rename(columns={
    "counts_4": "counts_x",
    "counts_2": "counts_y",
    "businesses_5": "counts_x_6",
    "counts_3": "counts_y_8",
    "counts_0": "businesses"
})

# The target schema expects:
# ['zipcode': int,
#  'businesses_x': string,
#  'counts_x': int,
#  'businesses_y': string,
#  'counts_y': int,
#  'businesses_x_5': string,
#  'counts_x_6': int,
#  'businesses_y_7': string,
#  'counts_y_8': int,
#  'boro': string,
#  'businesses': int]

# Ensure correct dtypes
df["zipcode"] = df["zipcode"].astype(int)
df["counts_x"] = df["counts_x"].fillna(0).astype(int)
df["counts_y"] = df["counts_y"].fillna(0).astype(int)
df["counts_x_6"] = df["counts_x_6"].fillna(0).astype(int)
df["counts_y_8"] = df["counts_y_8"].fillna(0).astype(int)
df["businesses"] = df["businesses"].fillna(0).astype(int)

# For string columns, keep as string, fillna with empty string if needed
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