import pandas as pd

# Read source tables with index_col=0 to ignore the numerical index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_4.csv", index_col=0)

# Join Source4_38_0 and Source4_38_3 on placeID
join_0_3 = pd.merge(source0, source3, on="placeID", how="inner")

# Join the above result with Source4_38_1 on placeID
join_0_3_1 = pd.merge(join_0_3, source1, on="placeID", how="inner")

# Join the above result with Source4_38_2 on placeID
join_0_3_1_2 = pd.merge(join_0_3_1, source2, on="placeID", how="inner")

# Join the above result with Source4_38_4 on placeID
final_df = pd.merge(join_0_3_1_2, source4, on="placeID", how="inner")

# Write the final output with exact target schema column order
target_columns = ['placeID', 'Rpayment', 'latitude', 'longitude', 'the_geom_meter', 'name', 'address', 'city', 'state', 'country', 'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code', 'accessibility', 'price', 'url', 'Rambience', 'franchise', 'area', 'other_services', 'Rcuisine', 'hours', 'days', 'parking_lot']

final_df = final_df[target_columns]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_38/target_multisource_mcts.csv", index=False)