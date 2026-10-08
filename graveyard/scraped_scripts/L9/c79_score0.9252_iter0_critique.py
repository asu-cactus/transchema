import pandas as pd

# List of source file paths and their corresponding table names
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_79/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_38.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_39.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_40.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_41.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_42.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_43.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_44.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_45.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_46.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_47.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_48.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_49.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_50.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_51.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_52.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_53.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_54.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_55.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_56.csv",
]

# Read all source tables with index_col=0 to ignore the numerical index column
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Concatenate all dataframes (UNION)
result = pd.concat(dfs, ignore_index=True)

# Write to the target file path
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_79/target_multisource_mcts.csv", index=False)