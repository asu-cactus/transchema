import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)
pivoted = df0.groupby("Gender").size().reset_index(name='0')
pivoted['0'] = pivoted['0'].astype(int)
pivoted = pivoted[['Gender', '0']]
pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)