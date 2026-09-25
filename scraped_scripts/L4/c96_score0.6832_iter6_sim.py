import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

join_result = pd.merge(s2, s3, how='inner', on=['SubjectId', 'Split', 'Subject'], suffixes=('_2', '_3'))

# Sum corresponding numeric columns from both sides of the join
for col in ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
    join_result[col] = join_result[f"{col}_2"] + join_result[f"{col}_3"]

join_result = join_result[['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

union_result_1 = pd.concat([s0, s1], ignore_index=True)

final_df = pd.concat([union_result_1, join_result], ignore_index=True)

final_df['SubjectId'] = final_df['SubjectId'].astype(int)
final_df['Split'] = final_df['Split'].astype(int, errors='ignore') if final_df['Split'].dtype != int else final_df['Split']
final_df['Subject'] = final_df['Subject'].astype(int, errors='ignore') if final_df['Subject'].dtype != int else final_df['Subject']

final_df = final_df[['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)