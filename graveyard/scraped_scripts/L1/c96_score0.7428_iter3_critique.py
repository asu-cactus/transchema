import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Join on hero name columns
joined = pd.merge(df0, df1, left_on="name", right_on="hero_names", how="inner")

# Group by Publisher and count heroes
agg = joined.groupby("Publisher", dropna=False).agg(name_count=("name", "count")).reset_index()

# Convert Publisher string to categorical codes starting from 1
agg["Publisher"] = agg["Publisher"].astype("category").cat.codes + 1

# Select only the Publisher column as per target schema
result = agg[["Publisher"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)