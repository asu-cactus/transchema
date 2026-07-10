import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_4.csv", index_col=0)

join_01 = pd.merge(df0, df1, on="placeID", how="inner")
join_012 = pd.merge(join_01, df2, on="placeID", how="inner")
join_0123 = pd.merge(join_012, df3, on="placeID", how="inner")
join_result = pd.merge(join_0123, df4, on="placeID", how="inner")

cols = ['placeID', 'Rpayment', 'latitude', 'longitude', 'the_geom_meter', 'name', 'address', 'city', 'state', 'country', 'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code', 'accessibility', 'price', 'url', 'Rambience', 'franchise', 'area', 'other_services', 'Rcuisine', 'hours', 'days', 'parking_lot']

result = join_result[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_38/target_multisource_mcts.csv")