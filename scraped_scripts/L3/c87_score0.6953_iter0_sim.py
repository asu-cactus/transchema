import pandas as pd

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_2.csv", index_col=0)
result = df2.groupby("Rank").size().reset_index(name='0')
result['Rank'] = result['Rank'].astype(int)
result['0'] = result['0'].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_87/target_multisource_mcts.csv", index=False)