import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="COD_PERSONA", how="inner")

result = pd.DataFrame()
result["COD_INTERV"] = merged["COD_INTERV"].astype(str)
result["estado_cli"] = merged["estado_cli"].astype(str)
result["COD_PERSONA"] = merged["COD_PERSONA"].astype(int)
result["COD_AREANEGO"] = merged["COD_AREANEGO"].astype(int)
result["COD_EDAD"] = merged["COD_EDAD"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_13/target_multisource_mcts.csv", index=False)