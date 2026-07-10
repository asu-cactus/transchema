import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_54/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_54/training_1.csv", index_col=0)

df = pd.merge(df0, df1[['ID', 'sex']], on='ID')[['sex', 'G1', 'G2', 'G3']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_54/target_multisource_mcts.csv", index=False)