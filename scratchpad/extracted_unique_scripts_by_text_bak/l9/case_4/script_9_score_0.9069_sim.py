import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_4/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_4/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby('purpose', as_index=False).size().rename(columns={'size':'purpose'})

# The target schema is ['purpose': integer], but the target examples show purpose as integer values.
# The groupby count is the count of rows per purpose, but the target schema expects 'purpose' column.
# The partial plan suggests grouping by purpose, so the output is the count of rows per purpose.
# However, the target schema is just 'purpose' column, so the count should be the aggregated value.
# The target examples show two columns, but the schema shows only one column 'purpose'.
# The examples show two columns, but the schema only one column 'purpose'.
# This suggests the target table has one column 'purpose' with integer values.
# The partial plan shows join on purpose columns and group by purpose.
# Since all sources have only 'purpose' column, union and group by purpose to count occurrences.
# So the final output is a dataframe with columns: 'purpose' and the count of occurrences.
# But the target schema is only 'purpose' column.
# So we output the grouped 'purpose' column with the count as the value.
# The target examples show two columns, but the schema only one column 'purpose'.
# Possibly the target examples show index and purpose column.
# So we output the grouped dataframe with 'purpose' and the count as 'purpose' column.
# To match the target schema, rename the count column to 'purpose'.

result = df_all.groupby('purpose', as_index=False).size()
result.columns = ['purpose', 'count']
result = result.rename(columns={'count':'purpose'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_4/target_multisource_mcts.csv", index=False)