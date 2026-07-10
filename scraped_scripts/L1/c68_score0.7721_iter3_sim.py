import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)

df_union['V_GENE'] = df_union['V_CALL'].str.split('-').str[0]

result = df_union[['V_GENE']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)