import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_23/training_3.csv", index_col=0)

j1 = pd.merge(s2, s3, on="placeID", how="inner")
j2 = pd.merge(j1, s0, on="placeID", how="inner")
j3 = pd.merge(j2, s1, on="placeID", how="inner")

cols = ['placeID', 'Rcuisine', 'latitude', 'longitude', 'the_geom_meter', 'name', 'address', 'city', 'state', 'country', 'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code', 'accessibility', 'price', 'url', 'Rambience', 'franchise', 'area', 'other_services', 'hours', 'days', 'parking_lot']
result = j3[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_23/target_multisource_mcts.csv", index=False)