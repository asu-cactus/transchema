import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_72/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_72/training_1.csv", index_col=0)

# Normalize city columns: strip spaces and lowercase
source0["city"] = source0["city"].str.strip().str.lower()
source1["city"] = source1["city"].str.strip().str.lower()

merged = pd.merge(source0, source1, on="city", how="inner")

agg = merged.groupby(["city", "type"], as_index=False)["fare"].mean()

# If needed, capitalize city and type to match target format (not explicitly required, so keep as is)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_72/target_multisource_mcts.csv", index=False)