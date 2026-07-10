import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)
pivot = df.groupby('Gender').size().reset_index(name='0')
pivot['0'] = pivot['0'].astype(int)
pivot = pivot[['Gender', '0']]
pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)