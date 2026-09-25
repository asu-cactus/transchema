import pandas as pd

# Load source 0 with index column
source0_path = 'autopipeline-benchmarks/github-pipelines/length1_42/test_0.csv'
source0 = pd.read_csv(source0_path, index_col=0)

# Load source 1 with index column
source1_path = 'autopipeline-benchmarks/github-pipelines/length1_42/test_1.csv'
source1 = pd.read_csv(source1_path, index_col=0)

# Join source 0 and source 1 on item_id to get movie titles
joined_df = pd.merge(source0, source1[['item_id', 'movie title']], on='item_id', how='left')

# Save to final target file
output_path = 'autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts_recovery_test_val.csv'
joined_df.to_csv(output_path, index=False)