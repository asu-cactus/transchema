import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
df_all['zip_code'] = df_all['zip_code'].astype(int)
result = df_all.groupby('zip_code', as_index=False).size()
result.columns = ['zip_code', 'count']
result = result.rename(columns={'count': 'zip_code'})
result['zip_code'] = result['zip_code'].astype(int)
result = result.rename(columns={'zip_code': 'zip_code', 'zip_code': 'zip_code'})  # no change, just clarity

# The target schema is ['zip_code': integer], but target examples show counts per zip_code.
# The target examples show the count as the value in the zip_code column, so we must rename count column to zip_code.
# Actually, the target examples show zip_code as the index and the value as count, so the target schema is just one column named zip_code with integer values representing counts per zip_code.
# So we rename the count column to zip_code to match the target schema.

result = result.rename(columns={'zip_code': 'zip_code'})
result = result[['zip_code']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_52/target_multisource_mcts.csv", index=False)