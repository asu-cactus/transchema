import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

agg0 = df0.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA':'sum', 'AB':'sum', 'H':'sum', 'TB':'sum', 'BB':'sum', 'SF':'sum', 'HBP':'sum'
})
agg1 = df1.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA':'sum', 'AB':'sum', 'H':'sum', 'TB':'sum', 'BB':'sum', 'SF':'sum', 'HBP':'sum'
})
agg2 = df2.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA':'sum', 'AB':'sum', 'H':'sum', 'TB':'sum', 'BB':'sum', 'SF':'sum', 'HBP':'sum'
})
agg3 = df3.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA':'sum', 'AB':'sum', 'H':'sum', 'TB':'sum', 'BB':'sum', 'SF':'sum', 'HBP':'sum'
})

union_df = pd.concat([agg0, agg1, agg2, agg3], ignore_index=True)

final_agg = union_df.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA':'sum', 'AB':'sum', 'H':'sum', 'TB':'sum', 'BB':'sum', 'SF':'sum', 'HBP':'sum'
})

final_agg = final_agg[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

final_agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)