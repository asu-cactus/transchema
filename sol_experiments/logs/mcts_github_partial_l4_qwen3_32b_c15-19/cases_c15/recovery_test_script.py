import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_15/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_15/test_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_15/test_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_15/test_3.csv', index_col=0)

joined_df03 = source0.merge(source3, on='COD_PERSONA', how='inner')
final_df = joined_df03.merge(source2, left_on='COD_OFICIPAL', right_on='COD_OFICI', how='inner')

final_df[['COD_INTERV', 'estado_cli', 'COD_OFICI', 'COD_NIVELOFIC']].to_csv(
    'autopipeline-benchmarks/github-pipelines/length4_15/target_multisource_mcts_recovery_test_val.csv', index=False
)