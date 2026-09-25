import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Normalize city strings in both dataframes: strip whitespace and lowercase
df0["city"] = df0["city"].str.strip().str.lower()
df1["city"] = df1["city"].str.strip().str.lower()

# Group by city in df0 to get average fare
grouped = df0.groupby("city", as_index=False).agg(average_fare=("fare", "mean"))

# Join df1 with grouped average fare on city
merged = pd.merge(df1, grouped, how="inner", on="city")

# Restore city casing to original from df1 (optional, but target examples show capitalized city names)
# Since we lost original casing by lowercasing, we can get original city names from df1 before lowercasing
# To do this, we can create a mapping from lowercase city to original city in df1 before lowercasing

# Re-read df1 without lowercasing to get original city names
df1_original = pd.read_csv(source1_path, index_col=0)
city_mapping = dict(zip(df1_original["city"].str.strip().str.lower(), df1_original["city"].str.strip()))

# Map back to original city names
merged["city"] = merged["city"].map(city_mapping)

# Cast columns to correct types
merged["driver_count"] = merged["driver_count"].astype("Int64")
merged["type"] = merged["type"].astype(str)
merged["city"] = merged["city"].astype(str)
merged["average_fare"] = merged["average_fare"].astype(float)

result = merged[["city", "driver_count", "type", "average_fare"]]

result.to_csv(target_path, index=False)