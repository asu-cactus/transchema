import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)
df['V_GENE'] = df['V_CALL'].str.split('*').str[0]
result = df[['V_GENE']].drop_duplicates().reset_index(drop=True)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)