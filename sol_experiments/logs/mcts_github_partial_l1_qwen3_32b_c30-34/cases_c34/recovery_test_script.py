import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_34/test_0.csv"
df = pd.read_csv(source_path, index_col=0)
df = df.rename(columns={'J_CALL': 'V_GENE'})
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts_recovery_test_val.csv", index=False)