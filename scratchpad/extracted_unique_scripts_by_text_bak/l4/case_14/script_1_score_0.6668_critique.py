import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_3.csv", index_col=0)

join_0_3 = pd.merge(source0, source3, on="COD_PERSONA", how="inner")

join_0_3_1 = pd.merge(
    join_0_3,
    source1,
    how="inner",
    left_on=["COD_IDCONTRA", "COD_PERSONA"],
    right_on=["COD_IDCONTRA", "COD_PERSONA"],
)

join_all = pd.merge(
    join_0_3_1,
    source2,
    how="inner",
    left_on="COD_OFICIPAL",
    right_on="COD_OFICI",
)

grouped = (
    join_all.groupby(["COD_INTERV", "estado_cli", "COD_EDAD"], dropna=False, as_index=False)
    .agg(
        COD_OFICIPAL=("COD_OFICIPAL", "first"),
        COD_SEGLOBAL=("COD_SEGLOBAL", "first"),
    )
)

# Cast columns to correct types
grouped["COD_INTERV"] = grouped["COD_INTERV"].astype(str)
grouped["estado_cli"] = grouped["estado_cli"].astype(str)
grouped["COD_EDAD"] = pd.to_numeric(grouped["COD_EDAD"], errors="coerce").astype("Int64")
grouped["COD_OFICIPAL"] = pd.to_numeric(grouped["COD_OFICIPAL"], errors="coerce").astype("Int64")
grouped["COD_SEGLOBAL"] = pd.to_numeric(grouped["COD_SEGLOBAL"], errors="coerce").astype("Int64")

# Reorder columns to match target schema
result = grouped[["COD_INTERV", "estado_cli", "COD_EDAD", "COD_OFICIPAL", "COD_SEGLOBAL"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_14/target_multisource_mcts.csv", index=False)