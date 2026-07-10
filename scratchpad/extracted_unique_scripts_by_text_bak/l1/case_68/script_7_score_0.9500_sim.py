import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)
df0 = df0[['V_CALL']]
df0 = df0.rename(columns={'V_CALL': 'V_GENE'})
df0['V_GENE'] = df0['V_GENE'].str.split('-').str[0]
df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)