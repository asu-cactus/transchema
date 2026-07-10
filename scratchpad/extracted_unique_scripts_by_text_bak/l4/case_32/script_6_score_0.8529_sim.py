import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)

join_3_0 = pd.merge(source3, source0, on="County", suffixes=('_r1401', '_r1403_x'))
join_3_0 = join_3_0.rename(columns={"r1403": "r1403_x", "r1401": "r1401"})

join_3_0_2 = pd.merge(join_3_0, source2, on="County")
join_3_0_2 = join_3_0_2.rename(columns={"r1402": "r1402"})

join_all = pd.merge(join_3_0_2, source4, on="County", suffixes=('', '_r1403_y'))
join_all = join_all.rename(columns={"r1403": "r1403_y"})

result = join_all[["County", "r1401", "r1402", "r1403_x", "r1403_y"]]

result = result.groupby(["County", "r1401", "r1402", "r1403_x", "r1403_y"], dropna=False).size().reset_index().drop(columns=0)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv", index=False)