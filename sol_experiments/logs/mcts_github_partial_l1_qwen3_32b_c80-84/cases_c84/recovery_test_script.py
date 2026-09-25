import pandas as pd

source_path = 'autopipeline-benchmarks/github-pipelines/length1_84/test_0.csv'
target_path = 'autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts_recovery_test_val.csv'

df = pd.read_csv(source_path, index_col=0)
df['V_GENE'] = df['V_CALL'].str.split('*').str[0]
result = df[['V_GENE']]
result.to_csv(target_path, index=False)