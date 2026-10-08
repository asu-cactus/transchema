import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_69/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_69/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length2_69/target_multisource_mcts.csv"

source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

groupby_source1 = source1.groupby("city", as_index=False).size().rename(columns={"size": "driver_count"})

source0_projection = source0[["city", "driver_count"]]

result = pd.concat([groupby_source1, source0_projection], ignore_index=True)

result = result.groupby("city", as_index=False)["driver_count"].sum()

result["city"] = result["city"].astype(str)
result["driver_count"] = result["driver_count"].astype(int)

result.to_csv(output_path, index=False)