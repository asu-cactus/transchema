import pandas as pd
import numpy as np

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

variances = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    var = df['int_rate'].var(ddof=0)
    variances.append(var)

df_var = pd.DataFrame([variances], columns=[f"Source9_47_{i}" for i in range(len(variances))])

df_unpivot = df_var.melt(var_name='source', value_name='int_rate')

df_unpivot['int_rate'] = df_unpivot['int_rate'].round().astype('Int64')

df_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length9_47/target_multisource_mcts.csv", index=False)