import pandas as pd

src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_3.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_7.csv", index_col=0)

union_df = pd.concat([src3, src5, src6, src7], ignore_index=True)

result = union_df.groupby("ROW_WID", as_index=False)["ARPU"].mean()

result.rename(columns={"ARPU": "ARPU"}, inplace=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_28/target_multisource_mcts.csv", index=False)