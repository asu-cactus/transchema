import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_4.csv", index_col=0)

# The target table only has one column: Profit (float)
# Only src3 contains the Profit column.
# The partial plan says UNPIVOT, but here we only need to extract the Profit column from src3.
# No unpivot needed because Profit is already a single column.
# So just select Profit column from src3.

target = src3[['Profit']].copy()

target.to_csv("autopipeline-benchmarks/github-pipelines/length5_78/target_multisource_mcts.csv")