import pandas as pd

# Read all source tables with index_col=0 to ignore the numerical index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_4.csv", index_col=0)

# Join Source4_23_2 and Source4_23_3 on placeID
df = pd.merge(source2, source3, on="placeID", how="inner")

# Join with Source4_23_0 on placeID
df = pd.merge(df, source0, on="placeID", how="inner")

# Join with Source4_23_1 on placeID
df = pd.merge(df, source1, on="placeID", how="inner")

# Join with Source4_23_4 on placeID
df = pd.merge(df, source4, on="placeID", how="inner")

# Reorder columns to match target schema exactly
target_columns = ['placeID', 'Rcuisine', 'latitude', 'longitude', 'the_geom_meter', 'name', 'address', 'city', 'state', 'country', 'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code', 'accessibility', 'price', 'url', 'Rambience', 'franchise', 'area', 'other_services', 'hours', 'days', 'parking_lot']
df = df[target_columns]

# Write to output CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_23/target_multisource_mcts.csv", index=False)