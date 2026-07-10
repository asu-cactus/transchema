import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_17/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_17/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_17/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_17/training_3.csv", index_col=0)

unpivot_cols = ['des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ']
unpivoted = s3.melt(id_vars=['COD_OFICI'], value_vars=unpivot_cols, var_name='variable', value_name='value')

# We want to pivot back so that each COD_OFICI has one row with all these columns again, but the prompt says UNPIVOT as first step.
# Actually, the target schema expects these columns as separate columns, so unpivoting all these columns together is not correct.
# Instead, the partial plan says UNPIVOT, but the target schema has these columns as separate columns, so unpivoting all at once is not correct.
# The best interpretation is that the partial plan suggests unpivoting to align columns, but here the source 3 already has these columns.
# So we skip unpivoting and just use source 3 as is.

# So we will not unpivot source 3, but use it as is.

# Join Source2 and Source0 on COD_PERSONA
joined_0 = pd.merge(s2, s0, on='COD_PERSONA', how='inner')

# Join the above with Source3 on COD_OFICI
joined_1 = pd.merge(joined_0, s3, left_on='COD_OFICIPAL', right_on='COD_OFICI', how='inner')

# Select and rename columns to match target schema
result = joined_1[['COD_INTERV', 'estado_cli', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ']].copy()

# Cast columns to correct types
int_cols = ['des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ']
for col in int_cols:
    result[col] = pd.to_numeric(result[col], errors='coerce').astype('Int64')

result['COD_INTERV'] = result['COD_INTERV'].astype(str)
result['estado_cli'] = result['estado_cli'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_17/target_multisource_mcts.csv", index=False)