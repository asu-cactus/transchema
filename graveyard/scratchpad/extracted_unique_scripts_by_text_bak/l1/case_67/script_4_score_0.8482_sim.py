import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)
pivot_df = df0.groupby('user_id')[['sad.depressed', 'open.stressed']].mean().reset_index()
pivot_df = pivot_df.rename(columns={'sad.depressed': 'sad', 'open.stressed': 'stressed'})
pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)