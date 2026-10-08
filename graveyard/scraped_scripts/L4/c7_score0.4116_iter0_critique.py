import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_7/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_7/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_7/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_7/training_3.csv", index_col=0)

# Join Source0 and Source3 on COD_IDCONTRA and COD_PERSONA
joined_0_3 = pd.merge(
    src0,
    src3,
    on=["COD_IDCONTRA", "COD_PERSONA"],
    how="inner",
    suffixes=('_0', '_3')
)

# Join the above with Source2 on COD_PERSONA
joined_0_3_2 = pd.merge(
    joined_0_3,
    src2,
    on="COD_PERSONA",
    how="inner"
)

# Join the above with Source1 on COD_AREANEGO = cod_areanego
joined_all = pd.merge(
    joined_0_3_2,
    src1,
    left_on="COD_AREANEGO",
    right_on="cod_areanego",
    how="inner"
)

# Group by des_zona and COD_PERSONA, aggregate COD_AREANEGO by max
result = joined_all.groupby(
    ["des_zona", "COD_PERSONA"], dropna=False
).agg(
    COD_AREANEGO=pd.NamedAgg(column="COD_AREANEGO", aggfunc="max")
).reset_index()

# Rename COD_PERSONA to COD_PERSONA_x to match target schema
result = result.rename(columns={"COD_PERSONA": "COD_PERSONA_x"})

# Ensure correct dtypes
result["des_zona"] = result["des_zona"].astype(str)
result["COD_PERSONA_x"] = result["COD_PERSONA_x"].astype("Int64")
result["COD_AREANEGO"] = result["COD_AREANEGO"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_7/target_multisource_mcts.csv", index=False)