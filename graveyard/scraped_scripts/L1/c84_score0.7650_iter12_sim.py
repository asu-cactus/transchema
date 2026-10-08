import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)
result_df = union_df[['V_CALL']].rename(columns={'V_CALL': 'V_GENE'})

result_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)