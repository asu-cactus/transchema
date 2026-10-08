import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/training_4.csv", index_col=0)

final_df = pd.concat([s0, s1, s2, s3, s4], ignore_index=True)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_66/target_multisource_mcts.csv", index=False)