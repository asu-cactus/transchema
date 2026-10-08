import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_3.csv", index_col=0)

join_df = pd.merge(s0, s2, on="WarNum", suffixes=('_0', '_2'))

unpivot_rows = []
for col in ['TransTo_0', 'TransTo_2']:
    unpivot_rows.append(join_df[['WarNum', col]].rename(columns={col: 'TransTo'}))
join_unpivot_result = pd.concat(unpivot_rows, ignore_index=True)

union_1_3 = pd.concat([s1, s3], ignore_index=True)

final_df = pd.concat([join_unpivot_result, union_1_3], ignore_index=True)

final_df = final_df[['WarNum', 'TransTo']]
final_df['WarNum'] = final_df['WarNum'].astype('Int64')
final_df['TransTo'] = final_df['TransTo'].fillna(0).astype(int)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_58/target_multisource_mcts.csv", index=False)