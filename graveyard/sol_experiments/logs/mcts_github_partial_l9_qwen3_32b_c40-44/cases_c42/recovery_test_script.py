import pandas as pd

# Read all sources and drop unnamed index column
sources = []
for i in range(222):  # 0 to 221
    filename = f'autopipeline-benchmarks/github-pipelines/length9_42/training_{i}.csv'
    df = pd.read_csv(filename, index_col=0)
    sources.append(df)

# Union all sources
union_df = pd.concat(sources, ignore_index=True)

# Save to target file with target schema
union_df.to_csv('autopipeline-benchmarks/github-pipelines/length9_42/target_multisource_mcts_recovery_test_val.csv', index=False)