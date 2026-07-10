import pandas as pd

src_paths = {
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

# Load all source tables
dfs = [pd.read_csv(path, index_col=0) for path in src_paths.values()]

# Union all sources
df_union = pd.concat(dfs, ignore_index=True)

# Group by admit, gre, prestige and aggregate gpa by mean to remove duplicates and match target
df_grouped = df_union.groupby(['admit', 'gre', 'prestige'], as_index=False).agg({'gpa': 'mean'})

# Ensure correct dtypes as per target schema
df_grouped['admit'] = df_grouped['admit'].astype(int)
df_grouped['gre'] = df_grouped['gre'].astype(int)
df_grouped['gpa'] = df_grouped['gpa'].astype(float)
df_grouped['prestige'] = df_grouped['prestige'].astype(int)

# Reorder columns to match target schema if needed
df_grouped = df_grouped[['admit', 'gre', 'gpa', 'prestige']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_66/target_multisource_mcts.csv", index=False)