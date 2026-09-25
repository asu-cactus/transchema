import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)
result = union_df.rename(columns={"click": "0"})
result = result[["condition", "0"]]
result["condition"] = result["condition"].astype(int)
result["0"] = result["0"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)