import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

agg_df = df_all.groupby('Split', as_index=False).agg({
    'SubjectId': 'sum',
    'Subject': 'sum',
    'PA': 'sum',
    'AB': 'sum',
    'H': 'sum',
    'TB': 'sum',
    'BB': 'sum',
    'SF': 'sum',
    'HBP': 'sum'
})

agg_df = agg_df[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)