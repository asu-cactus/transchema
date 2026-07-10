import pandas as pd

# Read source tables with index_col=0 to ignore numerical index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_4.csv", index_col=0)

# Join Source4_23_2 and Source4_23_1 on placeID
result = pd.merge(source2, source1, on="placeID", how="inner")

# Join with Source4_23_0 on placeID
result = pd.merge(result, source0, on="placeID", how="inner")

# Join with Source4_23_3 on placeID
result = pd.merge(result, source3, on="placeID", how="inner")

# Join with Source4_23_4 on placeID
result = pd.merge(result, source4, on="placeID", how="inner")

# Reorder columns to match target schema exactly
target_columns = ['placeID', 'Rcuisine', 'latitude', 'longitude', 'the_geom_meter', 'name', 'address', 'city', 'state', 'country', 'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code', 'accessibility', 'price', 'url', 'Rambience', 'franchise', 'area', 'other_services', 'hours', 'days', 'parking_lot']

# The Rcuisine column comes from source3, so ensure it is present
# The parking_lot column comes from source0
# The hours and days columns come from source1

# Select and reorder columns
result = result[target_columns]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_23/target_multisource_mcts.csv", index=False)