import pandas as pd

# List all source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_78/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_38.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_39.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_40.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_41.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_42.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_43.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_44.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_45.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_46.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_47.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_48.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_49.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_50.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_51.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_52.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_53.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_54.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_55.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_56.csv",
]

# Read all source tables with index_col=0 to ignore the numerical index column
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Concatenate all dataframes vertically (UNION)
result = pd.concat(dfs, ignore_index=True)

# Write the final output to the target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_78/target_multisource_mcts.csv", index=False)