import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_1/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_all = df_all[['company_permalink', 'funded_year', 'raised_amount_usd']]

df_all = df_all.dropna(subset=['company_permalink', 'funded_year', 'raised_amount_usd'])

df_all['funded_year'] = df_all['funded_year'].astype(int)
df_all['raised_amount_usd'] = df_all['raised_amount_usd'].astype(float)

result = df_all.groupby(['company_permalink', 'funded_year'], as_index=False).agg({'raised_amount_usd':'sum'})

result['raised_amount_usd'] = result['raised_amount_usd'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_1/target_multisource_mcts.csv", index=False)