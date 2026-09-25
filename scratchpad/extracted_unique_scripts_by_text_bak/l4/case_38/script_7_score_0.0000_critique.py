import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_4.csv", index_col=0)

# Join all tables on placeID using inner joins to preserve multiplicity and avoid NaNs
df = df0.merge(df1, on="placeID", how="inner")
df = df.merge(df2, on="placeID", how="inner")
df = df.merge(df3, on="placeID", how="inner")
df = df.merge(df4, on="placeID", how="inner")

# Select columns in the exact order of the target schema
df = df[['placeID', 'Rpayment', 'latitude', 'longitude', 'the_geom_meter', 'name', 'address', 'city', 'state', 'country', 'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code', 'accessibility', 'price', 'url', 'Rambience', 'franchise', 'area', 'other_services', 'Rcuisine', 'hours', 'days', 'parking_lot']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_38/target_multisource_mcts.csv", index=False)