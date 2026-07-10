import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_4.csv", index_col=0)

# Drop duplicates on placeID in s4 to avoid row multiplication (Rpayment not in target)
s4_unique = s4.drop_duplicates(subset=["placeID"])

# Join s2 and s3 on placeID
df = s2.merge(s3, on="placeID", how="inner")

# Join s0 (parking_lot)
df = df.merge(s0, on="placeID", how="inner")

# Join s1 (hours, days)
df = df.merge(s1, on="placeID", how="inner")

# Join s4 (Rpayment) but drop Rpayment column after join
df = df.merge(s4_unique, on="placeID", how="inner")

# Drop Rpayment column as it's not in target schema
df = df.drop(columns=["Rpayment"])

# Reorder columns to match target schema
final_cols = [
    "placeID", "Rcuisine", "latitude", "longitude", "the_geom_meter", "name", "address",
    "city", "state", "country", "fax", "zip", "alcohol", "smoking_area", "dress_code",
    "accessibility", "price", "url", "Rambience", "franchise", "area", "other_services",
    "hours", "days", "parking_lot"
]

df = df[final_cols]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_23/target_multisource_mcts.csv", index=False)