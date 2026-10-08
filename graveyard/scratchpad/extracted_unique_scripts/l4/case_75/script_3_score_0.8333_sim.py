import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)

pivoted = df0.groupby('type').agg({'size':'mean', 'budget':'mean'}).reset_index()
pivoted.columns = ['type', 'a', 'b']

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)