import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_6/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_6/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_6/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_6/training_3.csv", index_col=0)

s0['estado_cli'] = s0['estado_cli'].map({'A':1, 'I':0}).fillna(0).astype(int)
s3['XTI_ESTADO'] = s3['XTI_ESTADO'].map({'A':1, 'I':0}).fillna(0).astype(int)
s3['QNU_ORDTIT'] = pd.to_numeric(s3['QNU_ORDTIT'], errors='coerce').fillna(0).astype(int)
s3['COD_INTERV'] = s3['COD_INTERV'].astype(str)

join_1_3 = pd.merge(s1, s3, how='inner', left_on=['COD_IDCONTRA','COD_PERSONA'], right_on=['COD_IDCONTRA','COD_PERSONA'], suffixes=('_x','_y'))

join_0 = pd.merge(join_1_3, s0, how='inner', left_on='COD_PERSONA', right_on='COD_PERSONA')

join_2 = pd.merge(join_0, s2, how='left', left_on='COD_OFICI', right_on='COD_OFICI')

join_2['COD_PERSONA_x'] = join_2['COD_PERSONA']
join_2['COD_PERSONA_y'] = join_2['COD_PERSONA']

cols = ['FAP_CONTR', 'COD_INTERV', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'estado_cli', 'COD_OFICI', 'COD_NIVELOFIC', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ', 'cod_areanego', 'des_areanego', 'COD_IDCONTRA', 'COD_PERSONA_x', 'IMP_CAPDIS', 'IMP_CAPINI', 'IMP_CAPPEN', 'COD_PERSONA_y', 'XTI_ESTADO', 'QNU_ORDTIT']

for c in ['COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'estado_cli', 'COD_OFICI', 'COD_NIVELOFIC', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'cod_areanego', 'COD_IDCONTRA', 'COD_PERSONA_x', 'IMP_CAPDIS', 'IMP_CAPINI', 'IMP_CAPPEN', 'COD_PERSONA_y', 'XTI_ESTADO', 'QNU_ORDTIT']:
    if c in join_2.columns:
        join_2[c] = pd.to_numeric(join_2[c], errors='coerce')

join_2['des_territ'] = join_2['des_territ'].astype(str)
join_2['des_areanego'] = join_2['des_areanego'].astype(str)

result = join_2[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_6/target_multisource_mcts.csv", index=False)