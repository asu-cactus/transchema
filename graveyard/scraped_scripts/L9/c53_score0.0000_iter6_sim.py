import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_10.csv", index_col=0)
s11 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_11.csv", index_col=0)
s12 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_12.csv", index_col=0)
s13 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_13.csv", index_col=0)
s14 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_14.csv", index_col=0)

joined = pd.merge(s2, s3, left_on='addr_state', right_on='addr_state', suffixes=('_2', '_3'))

unpivot_rows = []
for col in ['addr_state_2', 'addr_state_3']:
    unpivot_rows.append(joined[[col]].rename(columns={col: 'addr_state'}))
unpivot_result = pd.concat(unpivot_rows, ignore_index=True)

union_all = pd.concat([s0, s1, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, unpivot_result], ignore_index=True)

union_all['addr_state'] = union_all['addr_state'].astype(int)

union_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_53/target_multisource_mcts.csv", index=False)