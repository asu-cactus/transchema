import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_1.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)

g0 = s0.groupby("CANCEL_DT", dropna=False).agg(count_0=("ROW_WID", "count"))
g1 = s1.groupby("CANCEL_DT", dropna=False).agg(count_1=("ROW_WID", "count"))
g4 = s4.groupby("CANCEL_DT", dropna=False).agg(count_4=("ROW_WID", "count"))
g5 = s5.groupby("CANCEL_DT", dropna=False).agg(count_5=("ROW_WID", "count"))

df = pd.concat([g0, g1, g4, g5], axis=1)

df = df.reset_index()

df = df.rename(columns={"CANCEL_DT": "CANCEL_DT"})

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)