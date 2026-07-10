import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length4_75/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Aggregate df1 by school_name to get mean reading_score and math_score
agg_scores = df1.groupby("school_name")[["reading_score", "math_score"]].mean().reset_index()

# Join df0 with aggregated scores on school_name
merged = pd.merge(df0, agg_scores, on="school_name", how="inner")

# Group by 'type' and compute mean of reading_score and math_score
result = merged.groupby("type")[["reading_score", "math_score"]].mean().reset_index()

# Rename columns to match target schema
result = result.rename(columns={"reading_score": "a", "math_score": "b"})

result.to_csv(target_path, index=False)