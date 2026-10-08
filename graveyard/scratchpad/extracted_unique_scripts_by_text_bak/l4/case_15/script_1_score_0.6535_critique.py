import pandas as pd

# Read sources with index_col=0 as instructed
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_3.csv", index_col=0)

# Join Source4_15_0 and Source4_15_3 on COD_PERSONA
join_0_3 = pd.merge(src0, src3, how='inner', on='COD_PERSONA')

# Join the above with Source4_15_1 on COD_IDCONTRA and COD_PERSONA
join_0_3_1 = pd.merge(join_0_3, src1, how='inner', on=['COD_IDCONTRA', 'COD_PERSONA'])

# Join the above with Source4_15_2 on COD_OFICIPAL = COD_OFICI
join_all = pd.merge(join_0_3_1, src2, how='inner', left_on='COD_OFICIPAL', right_on='COD_OFICI')

# Group by COD_INTERV and estado_cli, aggregate COD_OFICI and COD_NIVELOFIC by max
grouped = join_all.groupby(['COD_INTERV', 'estado_cli'], as_index=False).agg({
    'COD_OFICI': 'max',
    'COD_NIVELOFIC': 'max'
})

# Ensure types and column order as target schema
result = grouped[['COD_INTERV', 'estado_cli', 'COD_OFICI', 'COD_NIVELOFIC']].copy()

result['COD_INTERV'] = result['COD_INTERV'].astype(str)
result['estado_cli'] = result['estado_cli'].astype(str)
result['COD_OFICI'] = pd.to_numeric(result['COD_OFICI'], errors='coerce').astype('Int64')
result['COD_NIVELOFIC'] = pd.to_numeric(result['COD_NIVELOFIC'], errors='coerce').astype('Int64')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_15/target_multisource_mcts.csv", index=False)