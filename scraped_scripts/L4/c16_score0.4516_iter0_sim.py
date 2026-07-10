import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_3.csv", index_col=0)

join_1_2 = pd.merge(s1, s2, on="COD_PERSONA", how="inner")
join_all = pd.merge(join_1_2, s3, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner")

result = join_all[["COD_INTERV", "estado_cli", "COD_OFICIPAL", "COD_SEGLOBAL", "COD_OFICI", "COD_NIVELOFIC"]]

result["COD_OFICIPAL"] = result["COD_OFICIPAL"].astype("Int64")
result["COD_SEGLOBAL"] = result["COD_SEGLOBAL"].astype("Int64")
result["COD_OFICI"] = result["COD_OFICI"].astype("Int64")
result["COD_NIVELOFIC"] = result["COD_NIVELOFIC"].astype("Int64")
result["COD_INTERV"] = result["COD_INTERV"].astype(str)
result["estado_cli"] = result["estado_cli"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_16/target_multisource_mcts.csv", index=False)