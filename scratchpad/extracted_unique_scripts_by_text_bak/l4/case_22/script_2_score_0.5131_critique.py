import pandas as pd

source_files = [
    "autopipeline-benchmarks/github-pipelines/length4_22/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_22/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_22/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_22/training_3.csv"
]

dfs = []
for file in source_files:
    df = pd.read_csv(file, index_col=0)
    dfs.append(df[['type_of_combined_shot', 'is_goal']])

df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby('type_of_combined_shot', dropna=False).agg(
    is_goal=('is_goal', 'mean'),
    shot_sum=('is_goal', 'size'),
    is_goal_count1=('is_goal', lambda x: (x == 1).sum())
).reset_index()

agg['shot_sum'] = agg['shot_sum'].astype(int)
agg['is_goal_count1'] = agg['is_goal_count1'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_22/target_multisource_mcts.csv", index=False)