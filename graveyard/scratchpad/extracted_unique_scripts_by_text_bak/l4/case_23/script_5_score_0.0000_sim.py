import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_4.csv", index_col=0)

df = s0.merge(s1, on="placeID", how="inner")
df = df.merge(s2, on="placeID", how="inner")
df = df.merge(s3, on="placeID", how="inner")
df = df.merge(s4, on="placeID", how="inner")

group_cols = [
    "parking_lot", "hours", "days", "city", "state", "country", "fax", "zip",
    "alcohol", "smoking_area", "dress_code", "accessibility", "price", "url",
    "Rambience", "franchise", "area", "other_services", "Rcuisine"
]

agg_df = df.groupby(
    ["placeID"] + group_cols,
    dropna=False,
    observed=False
).agg(
    latitude_min = ("latitude", "min"),
    latitude_max = ("latitude", "max"),
    longitude_min = ("longitude", "min"),
    longitude_max = ("longitude", "max"),
    placeID_count = ("placeID", "count")
).reset_index()

# For latitude and longitude, take the average of min and max to get a single value
agg_df["latitude"] = (agg_df["latitude_min"] + agg_df["latitude_max"]) / 2
agg_df["longitude"] = (agg_df["longitude_min"] + agg_df["longitude_max"]) / 2

# Drop the min/max columns
agg_df = agg_df.drop(columns=["latitude_min", "latitude_max", "longitude_min", "longitude_max", "placeID_count"])

# The_geom_meter, name, address columns come from s2, so merge them back on placeID
s2_sub = s2[["placeID", "the_geom_meter", "name", "address"]].drop_duplicates(subset=["placeID"])
result = agg_df.merge(s2_sub, on="placeID", how="left")

# Reorder columns to match target schema
final_cols = [
    "placeID", "Rcuisine", "latitude", "longitude", "the_geom_meter", "name", "address",
    "city", "state", "country", "fax", "zip", "alcohol", "smoking_area", "dress_code",
    "accessibility", "price", "url", "Rambience", "franchise", "area", "other_services",
    "hours", "days", "parking_lot"
]

result = result[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_23/target_multisource_mcts.csv", index=False)