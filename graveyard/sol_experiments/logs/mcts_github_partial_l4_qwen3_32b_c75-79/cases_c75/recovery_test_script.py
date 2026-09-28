import pandas as pd

# Load sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/test_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/test_1.csv", index_col=0)

# Join tables on school_name
merged = pd.merge(source0, source1, on="school_name", how="inner")

# Group by type and compute averages
result = merged.groupby("type", as_index=False).agg(
    a=("reading_score", "mean"),
    b=("math_score", "mean")
)

# Save to target
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts_recovery_test_val.csv", index=False)