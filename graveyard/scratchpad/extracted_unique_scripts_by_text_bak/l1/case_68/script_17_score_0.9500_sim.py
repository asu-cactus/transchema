import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)
df['V_GENE'] = df['V_CALL'].str.split('*').str[0].str.split('-').str[0]
df_target = df[['V_GENE']]
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)