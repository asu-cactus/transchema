import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_59/test_0.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts_recovery_test_val.csv"

df = pd.read_csv(source_path, index_col=0)
result = df.groupby("PRODUCTLINE")["SALES"].sum().reset_index()
result.to_csv(target_path, index=False)