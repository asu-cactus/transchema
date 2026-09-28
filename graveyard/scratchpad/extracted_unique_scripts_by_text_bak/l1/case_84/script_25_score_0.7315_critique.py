import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)
result = df['V_CALL'].str.split('*').str[0].drop_duplicates().reset_index(drop=True).to_frame(name='V_GENE')
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)