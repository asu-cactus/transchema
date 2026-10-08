import pandas as pd

files = [
    "autopipeline-benchmarks/github-pipelines/length9_88/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_9.csv"
]

dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

agg_df = df_all.groupby('prestige').agg({
    'admit': 'sum',
    'gre': 'min',
    'gpa': 'max'
}).reset_index()

agg_df = agg_df[['admit', 'gre', 'gpa', 'prestige']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_88/target_multisource_mcts.csv", index=False)