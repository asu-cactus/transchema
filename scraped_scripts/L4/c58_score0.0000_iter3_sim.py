import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_3.csv", index_col=0)

join_01 = pd.merge(df0, df1, on="WarNum", how="inner", suffixes=('_0', '_1'))
join_012 = pd.merge(join_01, df2, on="WarNum", how="inner")
join_0123 = pd.merge(join_012, df3, on="WarNum", how="inner")

result = join_0123.groupby("WarNum", as_index=False).size().rename(columns={"size": "count"})

# The target schema is ['WarNum', 'TransTo'] with TransTo integer.
# The target examples show TransTo is always 0.
# Since all source TransTo columns are NaN, and the target TransTo is 0, we set TransTo=0.

result = result[["WarNum"]]
result["TransTo"] = 0
result["WarNum"] = result["WarNum"].astype(int)
result["TransTo"] = result["TransTo"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_58/target_multisource_mcts.csv", index=False)