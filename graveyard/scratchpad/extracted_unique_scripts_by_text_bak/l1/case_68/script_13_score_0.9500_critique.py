import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)
# Extract V_GENE by splitting on '*' first, then on '-' to get the gene family prefix
df0['V_GENE'] = df0['V_CALL'].str.split('*').str[0].str.split('-').str[0]
final = df0[['V_GENE']]
final.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)