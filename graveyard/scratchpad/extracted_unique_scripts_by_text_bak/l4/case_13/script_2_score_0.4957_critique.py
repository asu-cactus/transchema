import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_3.csv", index_col=0)

# Join Source4_13_0 and Source4_13_3 on COD_IDCONTRA
join_0_3 = pd.merge(source0, source3, on="COD_IDCONTRA", how="inner", suffixes=('_0', '_3'))

# Join Source4_13_1 and Source4_13_2 on COD_OFICIPAL = COD_OFICI
join_1_2 = pd.merge(source1, source2, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner", suffixes=('_1', '_2'))

# Join the above two on COD_PERSONA
final_join = pd.merge(join_0_3, join_1_2, on="COD_PERSONA", how="inner")

# Group by COD_INTERV, estado_cli, COD_PERSONA
# Aggregate COD_AREANEGO and COD_EDAD by taking first value
grouped = final_join.groupby(
    ['COD_INTERV', 'estado_cli', 'COD_PERSONA'], as_index=False
).agg({
    'COD_AREANEGO': 'first',
    'COD_EDAD': 'first'
})

# Ensure correct types and column order as target schema
result = pd.DataFrame()
result["COD_INTERV"] = grouped["COD_INTERV"].astype(str)
result["estado_cli"] = grouped["estado_cli"].astype(str)
result["COD_PERSONA"] = grouped["COD_PERSONA"].astype(int)
result["COD_AREANEGO"] = grouped["COD_AREANEGO"].astype(int)
result["COD_EDAD"] = grouped["COD_EDAD"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_13/target_multisource_mcts.csv", index=False)