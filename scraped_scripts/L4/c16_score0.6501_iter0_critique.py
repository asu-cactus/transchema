import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_3.csv", index_col=0)

# Join Source4_16_0 and Source4_16_1 on COD_IDCONTRA and COD_PERSONA
join_0_1 = pd.merge(s0, s1, on=["COD_IDCONTRA", "COD_PERSONA"], how="inner")

# Join the above with Source4_16_2 on COD_PERSONA
join_0_1_2 = pd.merge(join_0_1, s2, on="COD_PERSONA", how="inner")

# Join the above with Source4_16_3 on COD_OFICIPAL = COD_OFICI
join_all = pd.merge(join_0_1_2, s3, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner")

# Select relevant columns
result = join_all[["COD_INTERV", "estado_cli", "COD_OFICIPAL", "COD_SEGLOBAL", "COD_OFICI", "COD_NIVELOFIC"]]

# Group by COD_INTERV and estado_cli, aggregate integer columns by first()
result = result.groupby(["COD_INTERV", "estado_cli"], as_index=False).agg({
    "COD_OFICIPAL": "first",
    "COD_SEGLOBAL": "first",
    "COD_OFICI": "first",
    "COD_NIVELOFIC": "first"
})

# Ensure correct dtypes
result["COD_OFICIPAL"] = result["COD_OFICIPAL"].astype("Int64")
result["COD_SEGLOBAL"] = result["COD_SEGLOBAL"].astype("Int64")
result["COD_OFICI"] = result["COD_OFICI"].astype("Int64")
result["COD_NIVELOFIC"] = result["COD_NIVELOFIC"].astype("Int64")
result["COD_INTERV"] = result["COD_INTERV"].astype(str)
result["estado_cli"] = result["estado_cli"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_16/target_multisource_mcts.csv", index=False)