import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv"

source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

grouped_source0 = source0.groupby("right_index", as_index=False).agg({"0": "mean"}).rename(columns={"right_index": "0_x", "0": "0_y"})

source1 = source1.rename(columns={"0": "0_x"})
merged = pd.merge(grouped_source0, source1, left_on="0_x", right_index=True, how="inner")

result = merged[["0_x", "0_y"]]
result.to_csv(output_path, index=False)