import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)

df_union = pd.concat([df0], ignore_index=True)

pivoted = df_union.groupby('condition')['click'].sum().reset_index()

pivoted.columns = ['condition', '0']
pivoted['condition'] = pivoted['condition'].astype(int)
pivoted['0'] = pivoted['0'].astype(int)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)