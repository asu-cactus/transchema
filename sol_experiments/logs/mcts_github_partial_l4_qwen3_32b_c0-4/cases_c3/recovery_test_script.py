import pandas as pd

# Load all sources
source4_3_0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_3/test_0.csv', index_col=0, header=0)
source4_3_1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_3/test_1.csv', index_col=0, header=0)
source4_3_2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_3/test_2.csv', index_col=0, header=0)
source4_3_3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_3/test_3.csv', index_col=0, header=0)

# First join between Source4_3_2 and Source4_3_3
joined_1 = pd.merge(source4_3_2, source4_3_3, on='COD_PERSONA')

# Second join with Source4_3_1
joined_2 = pd.merge(joined_1, source4_3_1, on='COD_PERSONA')

# Final join with Source4_3_0
final_df = pd.merge(joined_2, source4_3_0, left_on='COD_OFICIPAL', right_on='COD_OFICI')

# Save the result
final_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_3/target_multisource_mcts_recovery_test_val.csv', index=False)