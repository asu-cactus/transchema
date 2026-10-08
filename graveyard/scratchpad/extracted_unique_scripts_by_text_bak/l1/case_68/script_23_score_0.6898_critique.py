import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)

df0['V_GENE'] = df0['V_CALL'].str.split('-', n=1).str[0]

df_result = df0[['V_GENE']].drop_duplicates().reset_index(drop=True)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)