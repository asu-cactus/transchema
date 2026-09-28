import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_3.csv", index_col=0)

# Join s1 and s2 on COD_OFICIPAL = COD_OFICI
s1_s2 = pd.merge(
    s1,
    s2.rename(columns={"COD_OFICI": "COD_OFICIPAL"}),
    on="COD_OFICIPAL",
    how="inner",
    suffixes=("", "_s2")
)

# Join the above with s0 on COD_PERSONA
s1_s2_s0 = pd.merge(
    s1_s2,
    s0[["COD_PERSONA", "COD_INTERV", "COD_IDCONTRA"]],
    on="COD_PERSONA",
    how="inner"
)

# Join the above with s3 on COD_IDCONTRA and COD_PERSONA
final_join = pd.merge(
    s1_s2_s0,
    s3[["COD_IDCONTRA", "COD_PERSONA"]],
    on=["COD_IDCONTRA", "COD_PERSONA"],
    how="inner"
)

# Select and rename columns to target schema
result = final_join[["COD_INTERV", "estado_cli", "COD_PERSONA", "COD_AREANEGO", "COD_EDAD"]]

# Group by leftmost columns and aggregate COD_AREANEGO and COD_EDAD by max (or first non-null)
result_grouped = result.groupby(
    ["COD_INTERV", "estado_cli", "COD_PERSONA"],
    dropna=False,
    as_index=False
).agg({
    "COD_AREANEGO": "max",
    "COD_EDAD": "max"
})

# Fix data types according to target schema
result_grouped["COD_INTERV"] = result_grouped["COD_INTERV"].astype("string")
result_grouped["estado_cli"] = result_grouped["estado_cli"].astype("string")
result_grouped["COD_PERSONA"] = pd.to_numeric(result_grouped["COD_PERSONA"], errors="coerce").astype("Int64")
result_grouped["COD_AREANEGO"] = pd.to_numeric(result_grouped["COD_AREANEGO"], errors="coerce").astype("Int64")
result_grouped["COD_EDAD"] = pd.to_numeric(result_grouped["COD_EDAD"], errors="coerce").astype("Int64")

# Write output
result_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_13/target_multisource_mcts.csv", index=False)