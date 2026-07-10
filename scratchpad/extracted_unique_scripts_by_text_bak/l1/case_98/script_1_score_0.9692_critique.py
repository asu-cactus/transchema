import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv"

source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

# Join source0 and source1 on source0.right_index and source1 index
merged = pd.merge(source1.rename(columns={"0": "0_x"}), source0.rename(columns={"0": "0_y"}), left_index=True, right_on="right_index", how="inner")

# Select and reorder columns to match target schema
result = merged[["0_x", "0_y"]]

result.to_csv(output_path, index=False)