import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_55/training_0.csv", index_col=0)
output = df0['J_CALL'].str.split('*').str[0].to_frame(name='V_GENE')
output.to_csv("autopipeline-benchmarks/github-pipelines/length1_55/target_multisource_mcts.csv", index=False)