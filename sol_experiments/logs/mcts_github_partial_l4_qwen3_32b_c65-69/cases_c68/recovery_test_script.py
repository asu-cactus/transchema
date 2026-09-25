import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_68/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_68/test_1.csv', index_col=0)

agg_df1 = df1.groupby('school_name', as_index=False).agg(
    mean_reading=('reading_score', 'mean'),
    mean_math=('math_score', 'mean')
)

merged_df = df0.merge(agg_df1, on='school_name')

merged_df['a'] = merged_df['type']
merged_df['b'] = merged_df['size'].astype(int)
merged_df['c'] = merged_df['budget'].astype(int)
merged_df['d'] = merged_df['mean_reading'].round(6)
merged_df['e'] = merged_df['mean_math'].round(6)

final_columns = ['school_name', 'a', 'b', 'c', 'd', 'e']
final_df = merged_df[final_columns]

final_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts_recovery_test_val.csv')