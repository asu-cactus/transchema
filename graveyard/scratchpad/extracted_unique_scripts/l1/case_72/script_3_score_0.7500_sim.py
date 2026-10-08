import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)
pivoted = df.pivot_table(index='condition', columns='condition', values='click', aggfunc='sum').reset_index()
pivoted.columns.name = None
pivoted = pivoted.rename(columns={0: '0'})
pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)