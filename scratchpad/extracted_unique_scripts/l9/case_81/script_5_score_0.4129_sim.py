import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_81/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_9.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

for i, df in enumerate(dfs):
    dfs[i] = df.astype({'admit': 'int64', 'gre': 'int64', 'gpa': 'float64', 'prestige': 'int64'})

concat_df = pd.concat(dfs, ignore_index=True)

agg_df = concat_df.groupby('prestige').agg({
    'admit': 'sum',
    'gre': 'mean',
    'gpa': 'max'
}).reset_index()

agg_df['admit'] = agg_df['admit'].astype(int)
agg_df['gre'] = agg_df['gre'].round().astype(int)
agg_df['gpa'] = agg_df['gpa'].astype(float)
agg_df['prestige'] = agg_df['prestige'].astype(int)

agg_df = agg_df[['admit', 'gre', 'gpa', 'prestige']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_81/target_multisource_mcts.csv", index=False)