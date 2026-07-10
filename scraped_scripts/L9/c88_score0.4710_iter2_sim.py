import pandas as pd

paths = [
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

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_result = pd.concat(dfs, ignore_index=True)

grouped = union_result.groupby(['admit', 'prestige'], as_index=False).agg(
    admit_count=('admit', 'count'),
    gre_avg=('gre', 'mean'),
    gpa_avg=('gpa', 'mean')
)

# The target schema is ['admit': int, 'gre': int, 'gpa': float, 'prestige': int]
# The partial plan aggregates count(admit), avg(gre), avg(gpa) grouped by admit and prestige.
# But the target schema expects columns: admit, gre, gpa, prestige
# The partial plan's group_by includes admit and prestige, but admit is also aggregated by count.
# This is ambiguous because admit is both grouped and counted.
# The target examples show admit as 0 or 1, not counts.
# So the partial plan's COUNT(admit) is likely a mistake or a misunderstanding.
# Instead, we should group by prestige and admit, and take average gre and gpa.
# But admit is a binary label, so grouping by admit and prestige is fine.
# The target schema expects admit as integer (0 or 1), gre as integer, gpa as float, prestige as integer.
# So we can keep admit and prestige as group keys, and average gre and gpa.
# But admit is a group key, so no aggregation on admit is needed.
# So the aggregation should be AVG(gre), AVG(gpa) grouped by admit and prestige.
# The partial plan's COUNT(admit) is not needed.

# Adjust aggregation accordingly:
grouped = union_result.groupby(['admit', 'prestige'], as_index=False).agg(
    gre=('gre', 'mean'),
    gpa=('gpa', 'mean')
)

# Round gre to int as target schema expects integer gre
grouped['gre'] = grouped['gre'].round().astype(int)
grouped['gpa'] = grouped['gpa'].astype(float)
grouped['admit'] = grouped['admit'].astype(int)
grouped['prestige'] = grouped['prestige'].astype(int)

grouped = grouped[['admit', 'gre', 'gpa', 'prestige']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_88/target_multisource_mcts.csv", index=False)