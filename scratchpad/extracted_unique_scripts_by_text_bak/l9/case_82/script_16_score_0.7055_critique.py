import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_82/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_union = pd.concat(dfs, ignore_index=True)

# Ensure correct dtypes
df_union = df_union.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

# Group by admit, gre, prestige and aggregate gpa by mean to remove duplicates
df_final = df_union.groupby(['admit', 'gre', 'prestige'], as_index=False).agg({'gpa': 'mean'})

# Reorder columns to match target schema order
df_final = df_final[['admit', 'gre', 'gpa', 'prestige']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_82/target_multisource_mcts.csv", index=False)