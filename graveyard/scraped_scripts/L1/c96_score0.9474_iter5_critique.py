import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Join on hero name columns
merged = pd.merge(df0, df1, left_on="name", right_on="hero_names", how="inner")

# Group by Publisher and count distinct hero names to avoid duplication
result = merged.groupby("Publisher", dropna=False).agg({"name": pd.Series.nunique}).reset_index()

# Rename count column to 'Publisher' as per target schema
result.columns = ["Publisher", "Publisher"]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)