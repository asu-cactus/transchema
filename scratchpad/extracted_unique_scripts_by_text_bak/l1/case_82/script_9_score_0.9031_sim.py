import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

pivoted = df.pivot_table(index='conservation_status', values='scientific_name', aggfunc='count').reset_index()
pivoted.columns = ['conservation_status', 'scientific_name']

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)