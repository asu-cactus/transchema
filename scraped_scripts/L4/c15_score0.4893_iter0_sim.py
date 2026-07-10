import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_3.csv", index_col=0)

join_0_3 = pd.merge(source0, source3, on="COD_PERSONA", how="inner")

join_all = pd.merge(join_0_3, source2, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner")

result = join_all[["COD_INTERV", "estado_cli", "COD_OFICIPAL", "COD_NIVELOFIC"]].copy()
result.rename(columns={"COD_OFICIPAL": "COD_OFICI"}, inplace=True)
result["COD_OFICI"] = result["COD_OFICI"].astype("Int64")
result["COD_NIVELOFIC"] = result["COD_NIVELOFIC"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_15/target_multisource_mcts.csv", index=False)