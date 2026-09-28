import pandas as pd

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_4.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_8.csv", index_col=0)

agg2 = s2.groupby("CANCEL_DT")["ROW_WID"].count().rename("count_2")
agg3 = s3.groupby("CANCEL_DT")["ROW_WID"].count().rename("count_3")
agg4 = s4.groupby("CANCEL_DT")["ROW_WID"].count().rename("count_4")
agg8 = s8.groupby("CANCEL_DT")["ROW_WID"].count().rename("count_8")

df = pd.concat([agg2, agg3, agg4, agg8], axis=1)

df["CANCEL_DT"] = df.index
df = df.reset_index(drop=True)

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_26/target_multisource_mcts.csv", index=False, columns=["CANCEL_DT"])