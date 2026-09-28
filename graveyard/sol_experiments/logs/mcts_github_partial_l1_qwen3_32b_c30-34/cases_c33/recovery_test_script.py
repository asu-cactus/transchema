import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/test_0.csv", index_col=0)
source0 = source0.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})

source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/test_1.csv", index_col=0)
source1 = source1.rename(columns={"Participation": "Participation_y", "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing", "Math": "Math_y", "Total": "Total"})

result = pd.merge(source0, source1, on="State", how="inner")
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_33/target_multisource_mcts_recovery_test_val.csv", index=False)