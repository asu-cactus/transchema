import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_3.csv", index_col=0)

count0 = s0.groupby("WarNum")["TransTo"].count()
count1 = s1.groupby("WarNum")["TransTo"].count()
count2 = s2.groupby("WarNum")["TransTo"].count()
count3 = s3.groupby("WarNum")["TransTo"].count()

all_warnums = pd.Index(count0.index).union(count1.index).union(count2.index).union(count3.index)

df = pd.DataFrame({"WarNum": all_warnums})
df = df.set_index("WarNum")

df["TransTo"] = (
    count0.reindex(all_warnums, fill_value=0)
    + count1.reindex(all_warnums, fill_value=0)
    + count2.reindex(all_warnums, fill_value=0)
    + count3.reindex(all_warnums, fill_value=0)
).astype(int)

df = df.reset_index()

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_58/target_multisource_mcts.csv", index=False)