import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_3.csv", index_col=0)

# Start from the dimension table with all counties
df = source2.merge(source3, on="County", how="left") \
            .merge(source0, on="County", how="left") \
            .merge(source1, on="County", how="left")

# Keep only columns in target schema: County, r1401, r1403
df = df[["County", "r1401", "r1403"]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_37/target_multisource_mcts.csv", index=False)