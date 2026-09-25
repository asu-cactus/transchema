import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_17/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_17/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_17/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_17/training_3.csv", index_col=0)

# Join Source1 and Source2 on COD_IDCONTRA and COD_PERSONA
joined_0 = pd.merge(s1, s2, on=['COD_IDCONTRA', 'COD_PERSONA'], how='inner')

# Join the above with Source0 on COD_PERSONA
joined_1 = pd.merge(joined_0, s0, on='COD_PERSONA', how='inner')

# Join the above with Source3 on COD_OFICIPAL = COD_OFICI
joined_2 = pd.merge(joined_1, s3, left_on='COD_OFICIPAL', right_on='COD_OFICI', how='inner')

# Select columns matching target schema
result = joined_2[['COD_INTERV', 'estado_cli', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ']].copy()

# Cast integer columns to Int64 nullable type
int_cols = ['des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ']
for col in int_cols:
    result[col] = pd.to_numeric(result[col], errors='coerce').astype('Int64')

# Cast string columns
result['COD_INTERV'] = result['COD_INTERV'].astype(str)
result['estado_cli'] = result['estado_cli'].astype(str)

# Group by COD_INTERV and estado_cli, aggregate other columns by max
agg_dict = {col: 'max' for col in int_cols}
result = result.groupby(['COD_INTERV', 'estado_cli'], as_index=False).agg(agg_dict)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_17/target_multisource_mcts.csv", index=False)