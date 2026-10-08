import pandas as pd
from scipy import stats

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_47/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_14.csv"
]

agg_dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    mode_val = df['int_rate'].mode()
    if mode_val.empty:
        # If no mode found, skip or treat as NaN
        mode_val = pd.Series([pd.NA])
    agg_dfs.append(pd.DataFrame({'int_rate': mode_val}))

union_df = pd.concat(agg_dfs, ignore_index=True)

result = union_df.groupby('int_rate', as_index=False).size().rename(columns={'size':'count'})

# The target schema only has 'int_rate' column, so we output unique int_rate values.
# The target examples show multiple int_rate values, so we output the grouped int_rate values.
# Since the target schema is only int_rate, we drop the count column.
final_df = result[['int_rate']]

final_df['int_rate'] = final_df['int_rate'].astype('Int64')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_47/target_multisource_mcts.csv", index=False)