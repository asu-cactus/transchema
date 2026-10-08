import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)

df0['V_GENE'] = df0['V_CALL'].str.split('*').str[0]
df1['V_GENE'] = df1['V_CALL'].str.split('*').str[0]

union_df = pd.concat([df0[['V_GENE']], df1[['V_GENE']]], ignore_index=True)
result = union_df.groupby('V_GENE', as_index=False).size().drop(columns='size')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)