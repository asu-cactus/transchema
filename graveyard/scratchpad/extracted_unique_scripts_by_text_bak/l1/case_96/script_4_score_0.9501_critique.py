import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Join on hero name columns: df0.name = df1.hero_names
joined = pd.merge(df0, df1, left_on="name", right_on="hero_names", how="inner")

# Group by Publisher and count the number of heroes (count of 'name')
result = joined.groupby("Publisher", dropna=False).agg({"name": "count"}).reset_index()

# Rename count column to 'Publisher' to match target schema
result = result.rename(columns={"name": "Publisher"})

# Select only the 'Publisher' column as per target schema
result = result[["Publisher"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)