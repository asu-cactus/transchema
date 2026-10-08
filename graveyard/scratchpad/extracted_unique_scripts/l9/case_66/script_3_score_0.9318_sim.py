import pandas as pd

paths_union = [
    "autopipeline-benchmarks/github-pipelines/length9_66/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_9.csv"
]

dfs_union = [pd.read_csv(p, index_col=0) for p in paths_union]
union_result = pd.concat(dfs_union, ignore_index=True)

source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_66/training_3.csv", index_col=0)

merged = pd.merge(
    source3,
    union_result,
    on=["admit", "gre", "prestige"],
    how="inner",
    suffixes=('_src3', '_union')
)

# After join, columns from source3 and union_result exist, but target schema is ['admit', 'gre', 'gpa', 'prestige']
# The 'gpa' column is present in both source3 and union_result, but join keys exclude 'gpa'.
# We must decide which 'gpa' to keep. Since join keys exclude 'gpa', merged will have both gpa_src3 and gpa_union columns.
# The target examples show 'gpa' as float, so we pick 'gpa' from source3 (gpa_src3) as it is smaller source (31 tuples) and likely more accurate.
# Alternatively, we can average or pick one. Here, pick gpa_src3 if exists, else gpa_union.

# Create final dataframe with target schema columns
final = pd.DataFrame()
final['admit'] = merged['admit']
final['gre'] = merged['gre']

# Prefer gpa from source3 if not null, else from union_result
final['gpa'] = merged['gpa_src3'].combine_first(merged['gpa_union'])

final['prestige'] = merged['prestige']

# Ensure correct dtypes
final = final.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_66/target_multisource_mcts.csv", index=False)