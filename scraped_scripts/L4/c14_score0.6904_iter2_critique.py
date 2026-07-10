import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_3.csv", index_col=0)

# Join Source0 and Source1 on COD_IDCONTRA and COD_PERSONA
join_0_1 = pd.merge(source0, source1, on=["COD_IDCONTRA", "COD_PERSONA"], how="inner")

# Join the above with Source3 on COD_PERSONA
join_0_1_3 = pd.merge(join_0_1, source3, on="COD_PERSONA", how="inner")

# Join the above with Source2 on COD_OFICIPAL = COD_OFICI
join_all = pd.merge(join_0_1_3, source2, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner")

# Select and convert columns as per target schema
df = join_all[["COD_INTERV", "estado_cli", "COD_EDAD", "COD_OFICIPAL", "COD_SEGLOBAL"]].copy()

df["COD_EDAD"] = pd.to_numeric(df["COD_EDAD"], errors="coerce").astype("Int64")
df["COD_OFICIPAL"] = pd.to_numeric(df["COD_OFICIPAL"], errors="coerce").astype("Int64")
df["COD_SEGLOBAL"] = pd.to_numeric(df["COD_SEGLOBAL"], errors="coerce").astype("Int64")
df["COD_INTERV"] = df["COD_INTERV"].astype(str)
df["estado_cli"] = df["estado_cli"].astype(str)

# Group by COD_INTERV and estado_cli, aggregate other columns by max
result = df.groupby(["COD_INTERV", "estado_cli"], as_index=False).agg({
    "COD_EDAD": "max",
    "COD_OFICIPAL": "max",
    "COD_SEGLOBAL": "max"
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_14/target_multisource_mcts.csv", index=False)