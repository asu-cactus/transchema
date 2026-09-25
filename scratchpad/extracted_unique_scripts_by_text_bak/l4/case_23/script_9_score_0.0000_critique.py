import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_0.csv", index_col=0)  # parking_lot
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_1.csv", index_col=0)  # hours, days
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_2.csv", index_col=0)  # main dimension
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_3.csv", index_col=0)  # Rcuisine
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_4.csv", index_col=0)  # Rpayment

# Join dimension with Rcuisine
j1 = pd.merge(s2, s3, on="placeID", how="inner")

# Join with Rpayment (multiple payments per placeID)
j2 = pd.merge(j1, s4, on="placeID", how="inner")

# Join with hours/days (multiple rows per placeID)
j3 = pd.merge(j2, s1, on="placeID", how="inner")

# Join with parking_lot
j4 = pd.merge(j3, s0, on="placeID", how="inner")

# Project columns exactly as target schema (exclude Rpayment)
cols = ['placeID', 'Rcuisine', 'latitude', 'longitude', 'the_geom_meter', 'name', 'address', 'city', 'state', 'country', 'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code', 'accessibility', 'price', 'url', 'Rambience', 'franchise', 'area', 'other_services', 'hours', 'days', 'parking_lot']

result = j4[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_23/target_multisource_mcts.csv", index=False)