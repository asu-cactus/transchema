import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv", index_col=0)

pivoted = df0.pivot_table(index='Source Zipcode', values='Counts', aggfunc='sum').reset_index()
pivoted['Source Zipcode'] = pivoted['Source Zipcode'].astype(int)
pivoted['Counts'] = pivoted['Counts'].astype(int)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)