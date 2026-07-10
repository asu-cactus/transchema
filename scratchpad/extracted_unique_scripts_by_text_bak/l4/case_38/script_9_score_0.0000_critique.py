import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_38/training_4.csv", index_col=0)

# Pivot Source4_38_3: aggregate Rpayment per placeID by concatenation (separated by space)
pivoted_s3 = s3.groupby('placeID', as_index=False).agg({'Rpayment': lambda x: ' '.join(sorted(x.unique()))})

# Join Source4_38_0 and Source4_38_1 on placeID
df = pd.merge(s0, s1, on='placeID', how='inner')

# Join with Source4_38_2 on placeID
df = pd.merge(df, s2, on='placeID', how='inner')

# Join with pivoted Source4_38_3 on placeID
df = pd.merge(df, pivoted_s3, on='placeID', how='inner')

# Join with Source4_38_4 on placeID (this will create multiple rows per placeID for different days)
df = pd.merge(df, s4, on='placeID', how='inner')

# Reorder columns exactly as target schema
df = df[['placeID', 'Rpayment', 'latitude', 'longitude', 'the_geom_meter', 'name', 'address', 'city', 'state', 'country', 'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code', 'accessibility', 'price', 'url', 'Rambience', 'franchise', 'area', 'other_services', 'Rcuisine', 'hours', 'days', 'parking_lot']]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_38/target_multisource_mcts.csv", index=False)