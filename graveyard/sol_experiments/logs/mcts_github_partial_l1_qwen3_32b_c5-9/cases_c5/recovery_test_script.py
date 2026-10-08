import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_5/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_5/test_1.csv', index_col=0)

joined = pd.merge(source0, source1, on='ProvinciaID')

joined[['ProvinciaID', 'ProvinciaNombre', 'RegionID', 'ComunaID', 'ComunaNombre']].to_csv(
    'autopipeline-benchmarks/github-pipelines/length1_5/target_multisource_mcts_recovery_test_val.csv', 
    index=False
)