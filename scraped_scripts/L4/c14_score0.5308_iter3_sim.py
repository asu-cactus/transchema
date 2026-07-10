import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_3.csv", index_col=0)

joined_3_2 = pd.merge(source3, source2, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner")

joined_3_2_0 = pd.merge(joined_3_2, source0, on="COD_PERSONA", how="inner")

joined_3_2_0_1 = pd.merge(joined_3_2_0, source1, on="COD_IDCONTRA", how="inner")

result = joined_3_2_0_1[["COD_INTERV", "estado_cli", "COD_EDAD", "COD_OFICIPAL", "COD_SEGLOBAL"]].copy()

result["COD_EDAD"] = pd.to_numeric(result["COD_EDAD"], errors='coerce').astype("Int64")
result["COD_OFICIPAL"] = pd.to_numeric(result["COD_OFICIPAL"], errors='coerce').astype("Int64")
result["COD_SEGLOBAL"] = pd.to_numeric(result["COD_SEGLOBAL"], errors='coerce').astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_14/target_multisource_mcts.csv", index=False)