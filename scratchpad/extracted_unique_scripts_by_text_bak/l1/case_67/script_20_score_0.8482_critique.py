import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)

df_renamed = df.rename(columns={'sad.depressed': 'sad', 'open.stressed': 'stressed'})

result = df_renamed.groupby('user_id', as_index=False)[['sad', 'stressed']].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)