import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_3/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce').astype('Int64')

grouped = df_all.groupby(['company_permalink', 'funded_year'], dropna=False, as_index=False)['raised_amount_usd'].sum()

grouped['raised_amount_usd'] = grouped['raised_amount_usd'].fillna(0).astype('int64')

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_3/target_multisource_mcts.csv", index=False)