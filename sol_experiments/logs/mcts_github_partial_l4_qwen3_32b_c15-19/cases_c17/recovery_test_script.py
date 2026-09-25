import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/test_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/test_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_17/test_3.csv', index_col=0)

temp1 = pd.merge(source2, source0, on='COD_PERSONA', how='inner')
temp2 = pd.merge(temp1, source3, left_on='COD_OFICIPAL', right_on='COD_OFICI', how='inner')

target = temp2[['COD_INTERV', 'estado_cli', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ']]

target.to_csv('autopipeline-benchmarks/github-pipelines/length4_17/target_multisource_mcts_recovery_test_val.csv')