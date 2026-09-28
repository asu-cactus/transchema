import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_40/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce').fillna(0).astype(int)
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce').fillna(0).astype(int)

grouped = df_all.groupby(['company_permalink', 'funded_year'], dropna=False, as_index=False)['raised_amount_usd'].sum()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_40/target_multisource_mcts.csv", index=False)