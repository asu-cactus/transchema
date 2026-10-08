import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_49/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Join Source9_49_4 and Source9_49_5 on emp_title equality (inner join on emp_title)
# Since both have only emp_title column, join on emp_title means intersection of emp_title values
# But joining on emp_title with no other columns results in duplicates or no new info.
# The partial plan suggests join on emp_title columns of Source9_49_4 and Source9_49_5.
# This join will produce rows where emp_title matches in both tables.
# We'll do an inner join on emp_title.

joined_4_5 = pd.merge(dfs[4], dfs[5], left_on='emp_title', right_on='emp_title', how='inner', suffixes=('_4', '_5'))

# After join, keep only one emp_title column (since both are same)
joined_4_5 = joined_4_5[['emp_title']]

# Replace dfs[4] and dfs[5] with the joined result for union
# Remove dfs[4] and dfs[5] from dfs list and add joined_4_5 instead
# But union expects all 15 sources, so we replace dfs[4] and dfs[5] with joined_4_5 and remove one to keep count same

# We'll remove dfs[5], replace dfs[4] with joined_4_5
dfs[4] = joined_4_5
del dfs[5]

# Now dfs has 14 dataframes: dfs[0..3], dfs[4]=joined_4_5, dfs[5..13] (original dfs[6..14])

# Union all dfs (now 14 dfs) vertically
result = pd.concat(dfs, ignore_index=True)

# Ensure emp_title is integer type as target schema
result['emp_title'] = result['emp_title'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_49/target_multisource_mcts.csv", index=False)