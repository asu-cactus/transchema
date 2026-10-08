import pandas as pd

source_files = {
    "Source9_66_0": "autopipeline-benchmarks/github-pipelines/length9_66/training_0.csv",
    "Source9_66_1": "autopipeline-benchmarks/github-pipelines/length9_66/training_1.csv",
    "Source9_66_2": "autopipeline-benchmarks/github-pipelines/length9_66/training_2.csv",
    "Source9_66_3": "autopipeline-benchmarks/github-pipelines/length9_66/training_3.csv",
    "Source9_66_4": "autopipeline-benchmarks/github-pipelines/length9_66/training_4.csv",
    "Source9_66_5": "autopipeline-benchmarks/github-pipelines/length9_66/training_5.csv",
    "Source9_66_6": "autopipeline-benchmarks/github-pipelines/length9_66/training_6.csv",
    "Source9_66_7": "autopipeline-benchmarks/github-pipelines/length9_66/training_7.csv",
    "Source9_66_8": "autopipeline-benchmarks/github-pipelines/length9_66/training_8.csv",
    "Source9_66_9": "autopipeline-benchmarks/github-pipelines/length9_66/training_9.csv",
}

# Read all source tables
dfs = [pd.read_csv(path, index_col=0) for path in source_files.values()]

# UNION all source tables
union_all = pd.concat(dfs, ignore_index=True)

# GROUP BY admit, gre, prestige and aggregate gpa by mean
target_df = union_all.groupby(['admit', 'gre', 'prestige'], as_index=False).agg({'gpa': 'mean'})

# Ensure correct column order and types
target_df = target_df[['admit', 'gre', 'gpa', 'prestige']]

target_df['admit'] = target_df['admit'].astype(int)
target_df['gre'] = target_df['gre'].astype(int)
target_df['gpa'] = target_df['gpa'].astype(float)
target_df['prestige'] = target_df['prestige'].astype(int)

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_66/target_multisource_mcts.csv", index=False)