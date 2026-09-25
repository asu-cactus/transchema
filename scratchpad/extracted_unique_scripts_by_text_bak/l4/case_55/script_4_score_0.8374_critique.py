import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_3.csv", index_col=0)

union_all = pd.concat([s0, s1, s2, s3], ignore_index=True)

result = union_all.groupby("WarNum", as_index=False).agg({"WhereFought": "min"})

result["WarNum"] = result["WarNum"].astype(int)
result["WhereFought"] = result["WhereFought"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_55/target_multisource_mcts.csv", index=False)