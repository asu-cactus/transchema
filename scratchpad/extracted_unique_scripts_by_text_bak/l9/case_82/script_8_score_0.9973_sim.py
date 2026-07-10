import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_82/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_result = pd.concat(dfs, ignore_index=True)

agg = union_result.groupby('prestige').agg(
    gpa_sum=pd.NamedAgg(column='gpa', aggfunc='sum'),
    gre_count=pd.NamedAgg(column='gre', aggfunc='count'),
    admit_min=pd.NamedAgg(column='admit', aggfunc='min')
).reset_index()

# The target schema is ['admit': int, 'gre': int, 'gpa': float, 'prestige': int]
# The partial plan aggregates SUM(gpa), COUNT(gre), MIN(admit) grouped by prestige.
# But the target examples show admit, gre, gpa, prestige as columns with no aggregation.
# This suggests the partial plan is not aligned with the target schema.
# Instead, since all source tables have the same schema as the target,
# and the target examples have 579 rows (more than any single source),
# the correct approach is to UNION ALL source tables (concatenate),
# then output the concatenated data as the target.

# So the partial plan is misleading or incomplete.
# We will produce the union of all source tables as the final target.

# Ensure correct dtypes
union_result = union_result.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

union_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_82/target_multisource_mcts.csv", index=False)