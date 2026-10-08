import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
pivoted = df.groupby('year').size().reset_index(name='0')
pivoted['year'] = pivoted['year'].astype(int)
pivoted['0'] = pivoted['0'].astype(int)
pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)