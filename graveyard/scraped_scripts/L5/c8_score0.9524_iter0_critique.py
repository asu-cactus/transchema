import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_8/training_1.csv", index_col=0)

# Join on school_name
joined = pd.merge(df0, df1, on="school_name", how="inner")

# Select school_name and size as math_score to match target schema
result = joined[["school_name", "size"]].drop_duplicates().rename(columns={"size": "math_score"})

# Ensure math_score is integer type
result["math_score"] = result["math_score"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_8/target_multisource_mcts.csv", index=False)