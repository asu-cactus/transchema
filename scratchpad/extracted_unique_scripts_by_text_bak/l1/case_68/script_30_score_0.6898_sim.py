import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)
df0['V_GENE'] = df0['V_CALL'].str.split('*').str[0].str.split('-').str[0]
result = df0.groupby('V_GENE', as_index=False).size().drop(columns='size')
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)