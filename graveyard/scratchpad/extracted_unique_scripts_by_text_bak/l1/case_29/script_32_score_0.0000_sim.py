import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

pivot = df.groupby('Gender').size().reset_index(name='0')

pivot['Gender'] = pivot['Gender'].astype(str)
pivot['0'] = pivot['0'].astype(int)

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)