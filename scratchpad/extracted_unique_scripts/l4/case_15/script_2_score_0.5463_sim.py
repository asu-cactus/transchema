import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_15/training_3.csv", index_col=0)

join_0_3 = pd.merge(src0, src3, how='inner', left_on='COD_PERSONA', right_on='COD_PERSONA')

join_all = pd.merge(join_0_3, src2, how='inner', left_on='COD_OFICIPAL', right_on='COD_OFICI')

result = join_all[['COD_INTERV', 'estado_cli', 'COD_OFICI', 'COD_NIVELOFIC']].copy()

result['COD_INTERV'] = result['COD_INTERV'].astype(str)
result['estado_cli'] = result['estado_cli'].astype(str)
result['COD_OFICI'] = pd.to_numeric(result['COD_OFICI'], errors='coerce').astype('Int64')
result['COD_NIVELOFIC'] = pd.to_numeric(result['COD_NIVELOFIC'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_15/target_multisource_mcts.csv", index=False)