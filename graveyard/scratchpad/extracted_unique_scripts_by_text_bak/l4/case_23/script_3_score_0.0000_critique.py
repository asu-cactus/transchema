import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_4.csv", index_col=0)

# Join Source4_23_0 and Source4_23_3 on placeID
join_0_3 = pd.merge(src0, src3, on="placeID", how="inner")

# Join with Source4_23_1 on placeID
join_0_3_1 = pd.merge(join_0_3, src1, on="placeID", how="inner")

# Join with Source4_23_2 on placeID
join_0_3_1_2 = pd.merge(join_0_3_1, src2, on="placeID", how="inner")

# Join with Source4_23_4 on placeID
final_join = pd.merge(join_0_3_1_2, src4, on="placeID", how="inner")

# The target schema does not include Rpayment, so exclude it
cols = ['placeID', 'Rcuisine', 'latitude', 'longitude', 'the_geom_meter', 'name', 'address', 'city', 'state', 'country', 'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code', 'accessibility', 'price', 'url', 'Rambience', 'franchise', 'area', 'other_services', 'hours', 'days', 'parking_lot']

final = final_join[cols]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_23/target_multisource_mcts.csv", index=False)