import pandas as pd

src_paths = {
    "Source9_85_0": "autopipeline-benchmarks/github-pipelines/length9_85/training_0.csv",
    "Source9_85_1": "autopipeline-benchmarks/github-pipelines/length9_85/training_1.csv",
    "Source9_85_2": "autopipeline-benchmarks/github-pipelines/length9_85/training_2.csv",
    "Source9_85_3": "autopipeline-benchmarks/github-pipelines/length9_85/training_3.csv",
    "Source9_85_4": "autopipeline-benchmarks/github-pipelines/length9_85/training_4.csv",
    "Source9_85_5": "autopipeline-benchmarks/github-pipelines/length9_85/training_5.csv",
    "Source9_85_6": "autopipeline-benchmarks/github-pipelines/length9_85/training_6.csv",
    "Source9_85_7": "autopipeline-benchmarks/github-pipelines/length9_85/training_7.csv",
    "Source9_85_8": "autopipeline-benchmarks/github-pipelines/length9_85/training_8.csv",
    "Source9_85_9": "autopipeline-benchmarks/github-pipelines/length9_85/training_9.csv",
}

# Read all source tables
dfs = [pd.read_csv(path, index_col=0) for path in src_paths.values()]

# Union all source tables
df_union = pd.concat(dfs, ignore_index=True)

# Group by the leftmost non-float columns that uniquely identify rows: 'admit', 'gre', 'prestige'
# Aggregate 'gpa' by mean
df_final = df_union.groupby(['admit', 'gre', 'prestige'], as_index=False).agg({'gpa': 'mean'})

# Ensure correct dtypes as per target schema
df_final = df_final.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_85/target_multisource_mcts.csv", index=False)