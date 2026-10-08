import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

final_df = pd.concat([s0, s1, s2, s3, s4], ignore_index=True)

final_df['hero'] = final_df['hero'].astype(str)
final_df['disadvantage'] = final_df['disadvantage'].astype(float)
final_df['winrate'] = final_df['winrate'].astype(float)
final_df['matches'] = final_df['matches'].astype(int)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)