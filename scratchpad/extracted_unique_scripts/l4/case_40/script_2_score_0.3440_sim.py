import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_3.csv", index_col=0)

join_result = pd.merge(df0, df1, on=['x','y'], suffixes=('_0','_1'))

union_result = pd.concat([df2, df3], ignore_index=True)

final_df = pd.concat([join_result[['x','y','label_0']], union_result], ignore_index=True)

final_df = final_df.rename(columns={'label_0':'label'})

final_df['x'] = final_df['x'].astype(float)
final_df['y'] = final_df['y'].astype(int)
final_df['label'] = final_df['label'].astype(str)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts.csv", index=False)