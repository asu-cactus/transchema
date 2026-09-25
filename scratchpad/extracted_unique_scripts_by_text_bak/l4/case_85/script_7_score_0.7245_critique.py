import pandas as pd

# List all source files (assuming 4 source files as per naming pattern)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_3.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0)[['crit_cn', 'critic']] for f in source_files]
df_union = pd.concat(dfs, ignore_index=True)

# Group by 'crit_cn' and count 'critic'
result = df_union.groupby('crit_cn', as_index=False)['critic'].count()
result.columns = ['crit_cn', 'critic']

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)