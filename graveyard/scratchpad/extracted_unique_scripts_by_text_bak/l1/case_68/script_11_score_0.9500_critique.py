import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)
df['V_GENE'] = df['V_CALL'].str.split('-', n=1).str[0]
result = df[['V_GENE']].reset_index(drop=True)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)