import pandas as pd

source_path = 'autopipeline-benchmarks/github-pipelines/length1_20/test_0.csv'
df = pd.read_csv(source_path, index_col=0)
grouped_df = df.groupby(['sex', 'smoker'], as_index=False).agg(
    total_bill=('total_bill', 'mean'),
    tip=('tip', 'mean'),
    size=('size', 'mean')
)
grouped_df.to_csv('autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts_recovery_test_val.csv')