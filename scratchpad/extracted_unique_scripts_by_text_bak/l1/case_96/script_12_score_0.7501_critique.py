import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Join on hero name
df = pd.merge(df0, df1, left_on="name", right_on="hero_names", how="inner")

# Group by Publisher and count number of heroes
agg = df.groupby("Publisher", dropna=False).size().reset_index(name="count")

# Convert Publisher string to categorical codes (integer)
agg["Publisher"] = agg["Publisher"].astype('category').cat.codes

# Keep only Publisher column as per target schema
agg = agg[["Publisher"]]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)