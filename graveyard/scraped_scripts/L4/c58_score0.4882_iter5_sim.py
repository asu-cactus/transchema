import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_3.csv", index_col=0)

join01 = pd.merge(s0, s1, on="WarNum", how="outer", suffixes=('_0', '_1'))
join012 = pd.merge(join01, s2, on="WarNum", how="outer")
join012 = join012.rename(columns={"TransTo": "TransTo_2"})
join0123 = pd.merge(join012, s3, on="WarNum", how="outer")
join0123 = join0123.rename(columns={"TransTo": "TransTo_3"})

df_unpivot = join0123.melt(id_vars=["WarNum"], value_vars=["TransTo_0", "TransTo_1", "TransTo_2", "TransTo_3"], value_name="TransTo")
result = df_unpivot[["WarNum", "TransTo"]].copy()
result["TransTo"] = result["TransTo"].fillna(0).astype(int)
result["WarNum"] = result["WarNum"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_58/target_multisource_mcts.csv", index=False)