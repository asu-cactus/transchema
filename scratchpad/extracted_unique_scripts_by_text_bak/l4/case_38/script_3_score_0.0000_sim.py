import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_4.csv", index_col=0)

union_result = pd.concat([source1, source2, source3, source4], ignore_index=True)

merged = pd.merge(source0, union_result, on="placeID", how="left")

cols = ['placeID', 'Rpayment', 'latitude', 'longitude', 'the_geom_meter', 'name', 'address', 'city', 'state', 'country', 'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code', 'accessibility', 'price', 'url', 'Rambience', 'franchise', 'area', 'other_services', 'Rcuisine', 'hours', 'days', 'parking_lot']

result = merged.reindex(columns=cols)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_38/target_multisource_mcts.csv", index=False)