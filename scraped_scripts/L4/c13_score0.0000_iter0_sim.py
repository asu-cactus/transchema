import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_2.csv", index_col=0)

join_01 = pd.merge(source0, source1, how='inner', on=['COD_PERSONA', 'COD_INTERV'])
join_012 = pd.merge(join_01, source2, how='inner', left_on='COD_OFICIPAL', right_on='COD_OFICI')

join_012 = join_012.rename(columns={'cod_areanego': 'COD_AREANEGO'})

result = join_012[['COD_INTERV', 'estado_cli', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD']]

result = result.astype({
    'COD_PERSONA': 'int',
    'COD_AREANEGO': 'int',
    'COD_EDAD': 'int',
    'COD_INTERV': 'str',
    'estado_cli': 'str'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_13/target_multisource_mcts.csv", index=False)