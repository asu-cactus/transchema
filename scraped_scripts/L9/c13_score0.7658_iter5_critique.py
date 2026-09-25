import pandas as pd

# Read all source tables with index_col=0
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_9.csv", index_col=0)

# Join all sources on ['Date', 'Jour'] using inner join
# Use suffixes to avoid column name collisions; pandas will add suffixes automatically
result = source0
result = result.merge(source1, on=['Date', 'Jour'], how='inner', suffixes=('_x', '_y'))
result = result.merge(source2, on=['Date', 'Jour'], how='inner', suffixes=('', '_x_37'))
result = result.merge(source3, on=['Date', 'Jour'], how='inner', suffixes=('', '_x_73'))
result = result.merge(source4, on=['Date', 'Jour'], how='inner', suffixes=('', '_x_109'))
result = result.merge(source5, on=['Date', 'Jour'], how='inner', suffixes=('', '_x_145'))
result = result.merge(source6, on=['Date', 'Jour'], how='inner', suffixes=('', '_x_181'))
result = result.merge(source7, on=['Date', 'Jour'], how='inner', suffixes=('', '_x_217'))
result = result.merge(source8, on=['Date', 'Jour'], how='inner', suffixes=('', '_x_253'))
result = result.merge(source9, on=['Date', 'Jour'], how='inner', suffixes=('', '_x_289'))

# The suffixes above are just placeholders; pandas will automatically rename columns with suffixes to avoid collisions.
# The target schema has many suffixes like _x, _y, _x_37, etc., so this matches the pattern.

# Write the final output with exact column names as in the target schema
# The merge preserves column names with suffixes, so no renaming needed.

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_13/target_multisource_mcts.csv", index=False)