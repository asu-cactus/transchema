import pandas as pd

# Load source data
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_87/test_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_87/test_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_87/test_3.csv", index_col=0)

# Join sources on [unit_code, year]
joined = source1.merge(source2, on=['unit_code', 'year'], how='outer')
joined = joined.merge(source3, on=['unit_code', 'year'], how='outer')

# Save output
joined.to_csv("autopipeline-benchmarks/github-pipelines/length4_87/target_multisource_mcts_recovery_test_val.csv")