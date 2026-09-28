import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_34/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_34/training_2.csv', index_col=0)

df0 = df0.rename(columns={'J_CALL': 'V_GENE'})
df1 = df1.rename(columns={'J_CALL': 'V_GENE'})
df2 = df2.rename(columns={'J_CALL': 'V_GENE'})

df_union = pd.concat([df0, df1, df2], ignore_index=True)

df_grouped = df_union.groupby('V_GENE', as_index=False).size()

df_grouped = df_grouped.rename(columns={'size': 'count'})

df_result = df_union[['V_GENE']]

df_result.to_csv('autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv', index=False)