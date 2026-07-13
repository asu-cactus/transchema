import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_28/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_28/test_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_28/test_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_28/test_3.csv', index_col=0)

combined = pd.concat([source0, source1, source2, source3], ignore_index=True)
result = combined.groupby('INCIDENT_TYPE', as_index=False).agg({
    'ULCS_NO': 'sum',
    'SCHOOL_YEAR': 'sum',
    'INCIDENT_COUNT': 'sum',
    'SCHOOL_ID': 'sum'
})
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts_recovery_test_val.csv', index=False)