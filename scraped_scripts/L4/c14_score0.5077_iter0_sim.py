import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_0.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_3.csv", index_col=0)

merged = pd.merge(src0, src3, on="COD_PERSONA", how="inner")

result = merged[["COD_INTERV", "estado_cli", "COD_EDAD", "COD_OFICIPAL", "COD_SEGLOBAL"]].copy()

result["COD_EDAD"] = pd.to_numeric(result["COD_EDAD"], errors="coerce").astype("Int64")
result["COD_OFICIPAL"] = pd.to_numeric(result["COD_OFICIPAL"], errors="coerce").astype("Int64")
result["COD_SEGLOBAL"] = pd.to_numeric(result["COD_SEGLOBAL"], errors="coerce").astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_14/target_multisource_mcts.csv", index=False)