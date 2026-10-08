import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_39/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_39/test_1.csv', index_col=0)

source0 = source0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

source1 = source1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

merged = pd.merge(source0, source1, on='State', how='inner')

merged.to_csv('autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts_recovery_test_val.csv')