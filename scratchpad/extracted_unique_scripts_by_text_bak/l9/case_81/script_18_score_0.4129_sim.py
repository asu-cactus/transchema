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
    "autopipeline-benchmarks/github-pipelines/length9_81/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_result = pd.concat(dfs, ignore_index=True)

agg = union_result.groupby('prestige').agg(
    gre_sum=pd.NamedAgg(column='gre', aggfunc='sum'),
    gpa_sum=pd.NamedAgg(column='gpa', aggfunc='sum'),
    admit_count=pd.NamedAgg(column='admit', aggfunc='count')
).reset_index()

agg['admit'] = agg['admit_count'].astype(int)
agg['gre'] = agg['gre_sum'].astype(int)
agg['gpa'] = agg['gpa_sum'].astype(float)
agg['prestige'] = agg['prestige'].astype(int)

result = agg[['admit', 'gre', 'gpa', 'prestige']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_81/target_multisource_mcts.csv", index=False)