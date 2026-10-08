import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_3.csv", index_col=0)

# Join Source4_13_0 and Source4_13_1 on COD_PERSONA only
join_01 = pd.merge(source0, source1, how='inner', on='COD_PERSONA')

# Join with Source4_13_2 on COD_OFICIPAL = COD_OFICI
join_012 = pd.merge(join_01, source2, how='inner', left_on='COD_OFICIPAL', right_on='COD_OFICI')

# Join with Source4_13_3 on COD_IDCONTRA and COD_PERSONA
join_0123 = pd.merge(join_012, source3, how='inner', on=['COD_IDCONTRA', 'COD_PERSONA'])

# Rename cod_areanego to COD_AREANEGO to match target schema
join_0123 = join_0123.rename(columns={'cod_areanego': 'COD_AREANEGO'})

# Select target columns
result = join_0123[['COD_INTERV', 'estado_cli', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD']]

# Cast types to match target schema
result = result.astype({
    'COD_INTERV': 'str',
    'estado_cli': 'str',
    'COD_PERSONA': 'int',
    'COD_AREANEGO': 'int',
    'COD_EDAD': 'int'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_13/target_multisource_mcts.csv", index=False)