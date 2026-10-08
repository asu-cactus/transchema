import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_98/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_98/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_98/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_98/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_98/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_98/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_98/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_98/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_98/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_98/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)

agg_df = union_df.groupby(['admit', 'prestige'], as_index=False).agg(
    gre_min=('gre', 'min'),
    gre_max=('gre', 'max'),
    gpa_min=('gpa', 'min'),
    gpa_max=('gpa', 'max')
)

# The target schema is ['admit', 'gre', 'gpa', 'prestige'] with gre and gpa as single values.
# The partial plan suggests min and max aggregations, but target examples show single gre and gpa values.
# We must decide how to produce single gre and gpa values from min and max.
# Since the target examples show single gre and gpa values, a reasonable approach is to take the average of min and max.

agg_df['gre'] = ((agg_df['gre_min'] + agg_df['gre_max']) / 2).round().astype(int)
agg_df['gpa'] = ((agg_df['gpa_min'] + agg_df['gpa_max']) / 2).astype(float)

result_df = agg_df[['admit', 'gre', 'gpa', 'prestige']]

result_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_98/target_multisource_mcts.csv", index=False)