import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

df_grouped = df.groupby('user_id', as_index=False)[['sad.depressed', 'open.stressed']].mean()

df_grouped = df_grouped.rename(columns={'sad.depressed': 'sad', 'open.stressed': 'stressed'})

df_grouped = df_grouped.astype({'user_id': int, 'sad': float, 'stressed': float})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)