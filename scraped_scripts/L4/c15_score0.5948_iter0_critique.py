import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_3.csv", index_col=0)

# Join Source0 and Source1 on COD_IDCONTRA and COD_PERSONA
join_0_1 = pd.merge(source0, source1, on=["COD_IDCONTRA", "COD_PERSONA"], how="inner")

# Join the above with Source3 on COD_PERSONA
join_0_1_3 = pd.merge(join_0_1, source3, on="COD_PERSONA", how="inner")

# Join the above with Source2 on COD_OFICIPAL = COD_OFICI
join_all = pd.merge(join_0_1_3, source2, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner")

# Group by COD_INTERV and estado_cli, aggregate COD_OFICI and COD_NIVELOFIC by min
grouped = join_all.groupby(["COD_INTERV", "estado_cli"], as_index=False).agg({
    "COD_OFICIPAL": "min",
    "COD_NIVELOFIC": "min"
})

# Rename COD_OFICIPAL to COD_OFICI to match target schema
grouped.rename(columns={"COD_OFICIPAL": "COD_OFICI"}, inplace=True)

# Ensure correct dtypes
grouped["COD_INTERV"] = grouped["COD_INTERV"].astype(str)
grouped["estado_cli"] = grouped["estado_cli"].astype(str)
grouped["COD_OFICI"] = grouped["COD_OFICI"].astype("Int64")
grouped["COD_NIVELOFIC"] = grouped["COD_NIVELOFIC"].astype("Int64")

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_15/target_multisource_mcts.csv", index=False)