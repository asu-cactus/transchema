import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

join_01 = pd.merge(source0, source1, on="County", how="inner")
join_02 = pd.merge(join_01, source2, on="County", how="inner")
join_03 = pd.merge(join_02, source3, on="County", how="inner")
join_04 = pd.merge(join_03, source4, on="County", how="inner")

# The resulting dataframe has columns: County, m1403, m1401, m1402, m1404
# Reorder columns to match target schema: ['County', 'm1401', 'm1402', 'm1403', 'm1404']
target = join_04[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)