import pandas as pd

# Read source tables with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/training_3.csv', index_col=0)

# Join Source4_17_0 and Source4_17_1 on COD_PERSONA
df = pd.merge(source0, source1, on='COD_PERSONA', how='inner')

# Join with Source4_17_2 on COD_IDCONTRA
df = pd.merge(df, source2, on='COD_IDCONTRA', how='inner')

# Join with Source4_17_3 on COD_INTERV = COD_OFICI
df = pd.merge(df, source3, left_on='COD_INTERV', right_on='COD_OFICI', how='inner')

# Select columns as per target schema
# Target schema: ['COD_INTERV', 'estado_cli', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ']

result = df[['COD_INTERV', 'estado_cli', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ']]

# Group by COD_INTERV and estado_cli to remove duplicates if any
result = result.groupby(['COD_INTERV', 'estado_cli'], as_index=False).first()

# Write to CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_17/target_multisource_mcts.csv', index=False)