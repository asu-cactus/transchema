import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_12/training_1.csv", index_col=0)

# Join on school_name
df_joined = pd.merge(df0, df1, on="school_name", how="inner")

# Group by school_name, aggregate size by first (size is constant per school)
result = df_joined.groupby("school_name", as_index=False)["size"].first()

# Rename size to reading_score to match target schema
result = result.rename(columns={"size": "reading_score"})

# Ensure reading_score is int
result["reading_score"] = result["reading_score"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_12/target_multisource_mcts.csv", index=False)