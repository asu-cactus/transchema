import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_55/training_0.csv", index_col=0)
df0['V_GENE'] = df0['J_CALL'].str.split('*').str[0]
result = df0.groupby('V_GENE', as_index=False).size().rename(columns={'size': 'count'})
output = result[['V_GENE']]
output.to_csv("autopipeline-benchmarks/github-pipelines/length1_55/target_multisource_mcts.csv", index=False)