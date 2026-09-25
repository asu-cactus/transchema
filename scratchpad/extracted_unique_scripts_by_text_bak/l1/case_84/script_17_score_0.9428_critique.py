import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)
result = df0[['V_CALL']].copy()
result['V_GENE'] = result['V_CALL'].str.split('*').str[0]
result = result[['V_GENE']]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)