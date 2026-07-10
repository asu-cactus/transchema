import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_2.csv", index_col=0)

merged = pd.merge(source2, source0, left_on="Country", right_on="Country Name", how="inner")

years = [str(y) for y in range(1960, 2016)]
melted = merged.melt(id_vars=["Rank"], value_vars=years, var_name="Year", value_name="Value")

melted = melted.dropna(subset=["Value"])

melted["Rank"] = melted["Rank"].astype(int)
melted["0"] = 1

result = melted[["Rank", "0"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_87/target_multisource_mcts.csv", index=False)