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

# The target schema is ['sub_grade': integer], but the target examples show sub_grade as integer values, 
# and the example values look like counts per sub_grade. The partial plan says PIVOT and GROUP_BY [sub_grade].
# The only column is sub_grade, so grouping by sub_grade and counting occurrences is the natural interpretation.

# However, the target schema is just ['sub_grade'], and the target examples show values like 27, 5, 44, which look like counts.
# So the output should be a table with sub_grade as the count of occurrences per sub_grade.

# Rename the count column to 'sub_grade' to match the target schema
result = result.rename(columns={'sub_grade': 'sub_grade'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_48/target_multisource_mcts.csv", index=False)