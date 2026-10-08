import pandas as pd

source_0 = pd.read_csv(
    'autopipeline-benchmarks/github-pipelines/length1_16/test_0.csv',
    index_col=0
)

result = source_0.groupby('CUSTOMERNAME', as_index=False)['ORDERNUMBER'].count()

result.to_csv(
    'autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts_recovery_test_val.csv',
    index=False
)