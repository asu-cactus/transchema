import pandas as pd

# Read source tables with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/training_3.csv', index_col=0)

# Join Source4_17_2 and Source4_17_3 on COD_INTERV = COD_OFICI
df = pd.merge(source2, source3, left_on='COD_INTERV', right_on='COD_OFICI', how='inner')

# Join with Source4_17_1 on COD_IDCONTRA
df = pd.merge(df, source1, on='COD_IDCONTRA', how='inner')

# Join with Source4_17_0 on COD_PERSONA
df = pd.merge(df, source0, on='COD_PERSONA', how='inner')

# Select and rename columns to match target schema:
# Target schema: ['COD_INTERV': string, 'estado_cli': string, 'des_ofici': integer, 'cod_cbc': integer, 'des_cbc': integer, 'cod_zona': integer, 'des_zona': integer, 'COD_TERRIT': integer, 'des_territ': integer]

# Columns from source3:
# des_ofici, cod_cbc, des_cbc, cod_zona, des_zona, COD_TERRIT, des_territ

# estado_cli from source0
# COD_INTERV from source2

result = df[['COD_INTERV', 'estado_cli', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ']]

# Group by COD_INTERV and estado_cli to ensure uniqueness (no aggregation needed as these are dimension attributes)
result = result.groupby(['COD_INTERV', 'estado_cli'], as_index=False).first()

# Write output
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_17/target_multisource_mcts.csv', index=False)