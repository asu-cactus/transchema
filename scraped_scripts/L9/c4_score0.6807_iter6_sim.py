import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_4/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_14.csv",
]

df_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_4/training_5.csv", index_col=0)
df_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_4/training_3.csv", index_col=0)

join_result = pd.merge(df_5, df_3, left_on="purpose", right_on="purpose", how="inner", suffixes=('_5', '_3'))

pivot_df = join_result.pivot_table(index=None, columns='purpose', aggfunc='size', fill_value=0)
pivot_df = pivot_df.reset_index(drop=True)

source_dfs = [pd.read_csv(p, index_col=0) for p in paths]

union_df = pd.concat(source_dfs + [pivot_df], ignore_index=True)

union_df = union_df.astype({'purpose': 'Int64'})

union_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_4/target_multisource_mcts.csv", index=False)