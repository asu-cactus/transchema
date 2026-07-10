import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_21/training_0.csv", index_col=0)
union_result = pd.concat([df0, df0], ignore_index=True)
target_df = union_result[['Major_category', 'Median']].copy()
target_df['Major_category'] = target_df['Major_category'].astype(str)
target_df['Median'] = target_df['Median'].astype(float)
target_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)