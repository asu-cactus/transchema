import pandas as pd

source1_37_0 = pd.read_csv(
    "autopipeline-benchmarks/github-pipelines/length1_37/test_0.csv",
    index_col=0
)
source1_37_1 = pd.read_csv(
    "autopipeline-benchmarks/github-pipelines/length1_37/test_1.csv",
    index_col=0
)

joined = pd.merge(
    source1_37_0,
    source1_37_1,
    on=["business_id", "date"],
    how="inner"
)

joined.to_csv(
    "autopipeline-benchmarks/github-pipelines/length1_37/target_multisource_mcts_recovery_test_val.csv",
    index=False
)