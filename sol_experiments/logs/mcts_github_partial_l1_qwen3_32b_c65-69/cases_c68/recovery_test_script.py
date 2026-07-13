import pandas as pd

source0_path = 'autopipeline-benchmarks/github-pipelines/length1_68/test_0.csv'
target_path = 'autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts_recovery_test_val.csv'

df = pd.read_csv(source0_path, index_col=0)
df['V_GENE'] = df['V_CALL'].str.split('-').str[0]
df = df[['V_GENE']]
df.to_csv(target_path, index=False)