import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)

union_df = pd.concat([df0, df1, df3, df5], ignore_index=True)

result = union_df.groupby("HOME_PASSED", as_index=False).agg({"ROW_WID": "count"})

result = result.rename(columns={"ROW_WID": "HOME_PASSED"})

result = result[["HOME_PASSED"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)