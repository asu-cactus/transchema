import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_48/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
result = df_all.groupby('sub_grade', as_index=False).size().rename(columns={'size': 'sub_grade'})
# The target schema is ['sub_grade': integer], and examples show sub_grade values as integers.
# The groupby count produces counts, but target examples show sub_grade values, not counts.
# So the groupby is just to group by sub_grade, but the target only has sub_grade column.
# So the output is unique sub_grade values, no aggregation count column.
# So we just need unique sub_grade values, sorted or not.
result = df_all[['sub_grade']].drop_duplicates().reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_48/target_multisource_mcts.csv", index=False)