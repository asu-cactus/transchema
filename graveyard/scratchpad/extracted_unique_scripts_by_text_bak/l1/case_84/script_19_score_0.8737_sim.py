import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)
df = df[['V_CALL']]
df = df.rename(columns={'V_CALL': 'V_GENE'})
df['V_GENE'] = df['V_GENE'].str.split('*').str[0]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)