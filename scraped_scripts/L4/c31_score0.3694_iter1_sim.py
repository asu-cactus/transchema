import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

source0['m1401'] = pd.NA
source0['m1402'] = pd.NA
source0['m1404'] = pd.NA
source0 = source0[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

source2['m1402'] = pd.NA
source2['m1403'] = pd.NA
source2['m1404'] = pd.NA
source2 = source2[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

source3['m1401'] = pd.NA
source3['m1403'] = pd.NA
source3['m1404'] = pd.NA
source3 = source3[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

source4['m1401'] = pd.NA
source4['m1402'] = pd.NA
source4['m1403'] = pd.NA
source4 = source4[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

union_result = pd.concat([source2, source3, source0, source4], ignore_index=True)

target = union_result.merge(source1, on='County', how='right')

target = target[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)