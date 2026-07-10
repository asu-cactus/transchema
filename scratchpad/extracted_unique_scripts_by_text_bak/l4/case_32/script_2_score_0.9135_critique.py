import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)

# Join Source1 and Source3 on County
join_1_3 = pd.merge(source1, source3, on="County", how="inner")

# Join with Source2 on County
join_1_3_2 = pd.merge(join_1_3, source2, on="County", how="inner")

# Join with Source0 on County, suffix r1403_x for source0
join_1_3_2_0 = pd.merge(join_1_3_2, source0, on="County", how="inner", suffixes=('', '_r1403_x'))
join_1_3_2_0 = join_1_3_2_0.rename(columns={"r1403": "r1403_x"})

# Join with Source4 on County, suffix r1403_y for source4
final_join = pd.merge(join_1_3_2_0, source4, on="County", how="inner", suffixes=('', '_r1403_y'))
final_join = final_join.rename(columns={"r1403": "r1403_y"})

# Select columns as per target schema
result = final_join[["County", "r1401", "r1402", "r1403_x", "r1403_y"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv", index=False)