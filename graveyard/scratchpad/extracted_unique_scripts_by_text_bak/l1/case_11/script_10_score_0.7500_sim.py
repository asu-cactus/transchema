import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv", index_col=0)

pivoted = df0.groupby('sex', as_index=False)['births'].sum()

pivoted['sex'] = pivoted['sex'].astype(str)
pivoted['births'] = pivoted['births'].astype(int)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts.csv", index=False)