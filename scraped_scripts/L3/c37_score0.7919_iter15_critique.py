import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_3.csv", index_col=0)

# Join Source2 (all counties) with Source3 (r1401)
result = pd.merge(source2, source3, on="County", how="left")

# Join with Source0 (r1403)
result = pd.merge(result, source0, on="County", how="left")

# Join with Source1 (r1402) - not needed in final output but must be used
result = pd.merge(result, source1, on="County", how="left")

# Select only columns in target schema
result = result[["County", "r1401", "r1403"]]

# Group by County to ensure uniqueness (no aggregation needed)
result = result.groupby("County", as_index=False).first()

# Filter out rows where both r1401 and r1403 are NaN (to match target row count)
result = result[~(result["r1401"].isna() & result["r1403"].isna())]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_37/target_multisource_mcts.csv", index=False)