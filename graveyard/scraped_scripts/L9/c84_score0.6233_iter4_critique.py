import pandas as pd

source_files = {
    "Source9_84_0": "autopipeline-benchmarks/github-pipelines/length9_84/training_0.csv",
    "Source9_84_1": "autopipeline-benchmarks/github-pipelines/length9_84/training_1.csv",
    "Source9_84_2": "autopipeline-benchmarks/github-pipelines/length9_84/training_2.csv",
    "Source9_84_3": "autopipeline-benchmarks/github-pipelines/length9_84/training_3.csv",
    "Source9_84_4": "autopipeline-benchmarks/github-pipelines/length9_84/training_4.csv",
    "Source9_84_5": "autopipeline-benchmarks/github-pipelines/length9_84/training_5.csv",
    "Source9_84_6": "autopipeline-benchmarks/github-pipelines/length9_84/training_6.csv",
    "Source9_84_7": "autopipeline-benchmarks/github-pipelines/length9_84/training_7.csv",
    "Source9_84_8": "autopipeline-benchmarks/github-pipelines/length9_84/training_8.csv",
    "Source9_84_9": "autopipeline-benchmarks/github-pipelines/length9_84/training_9.csv",
}

# Read all source tables
dfs = [pd.read_csv(path, index_col=0) for path in source_files.values()]

# Union all sources
df_union = pd.concat(dfs, ignore_index=True)

# Group by leftmost non-float columns (admit, gre, prestige), aggregate gpa by mean
df_final = df_union.groupby(['admit', 'gre', 'prestige'], as_index=False).agg({'gpa': 'mean'})

# Ensure correct dtypes
df_final = df_final.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_84/target_multisource_mcts.csv", index=False)