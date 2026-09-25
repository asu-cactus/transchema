import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)
union_df = union_df.astype({'condition': 'int64', 'click': 'int64'})

union_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv", index=False)