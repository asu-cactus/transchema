import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_71/test_0.csv"
source0 = pd.read_csv(source0_path, index_col=0)

target_df = (
    source0
    .groupby("Region", as_index=False)
    .agg({"Poblacion": "sum", "Superficie": "sum"})
)

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_71/target_multisource_mcts_recovery_test_val.csv", index=False)