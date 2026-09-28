import pandas as pd

# List all source file paths and their corresponding table names
source_files = {
    "Source9_78_0": "autopipeline-benchmarks/github-pipelines/length9_78/training_0.csv",
    "Source9_78_1": "autopipeline-benchmarks/github-pipelines/length9_78/training_1.csv",
    "Source9_78_2": "autopipeline-benchmarks/github-pipelines/length9_78/training_2.csv",
    "Source9_78_3": "autopipeline-benchmarks/github-pipelines/length9_78/training_3.csv",
    "Source9_78_4": "autopipeline-benchmarks/github-pipelines/length9_78/training_4.csv",
    "Source9_78_5": "autopipeline-benchmarks/github-pipelines/length9_78/training_5.csv",
    "Source9_78_6": "autopipeline-benchmarks/github-pipelines/length9_78/training_6.csv",
    "Source9_78_7": "autopipeline-benchmarks/github-pipelines/length9_78/training_7.csv",
    "Source9_78_8": "autopipeline-benchmarks/github-pipelines/length9_78/training_8.csv",
    "Source9_78_9": "autopipeline-benchmarks/github-pipelines/length9_78/training_9.csv",
    "Source9_78_10": "autopipeline-benchmarks/github-pipelines/length9_78/training_10.csv",
    "Source9_78_11": "autopipeline-benchmarks/github-pipelines/length9_78/training_11.csv",
    "Source9_78_12": "autopipeline-benchmarks/github-pipelines/length9_78/training_12.csv",
    "Source9_78_13": "autopipeline-benchmarks/github-pipelines/length9_78/training_13.csv",
    "Source9_78_14": "autopipeline-benchmarks/github-pipelines/length9_78/training_14.csv",
    "Source9_78_15": "autopipeline-benchmarks/github-pipelines/length9_78/training_15.csv",
    "Source9_78_16": "autopipeline-benchmarks/github-pipelines/length9_78/training_16.csv",
    "Source9_78_17": "autopipeline-benchmarks/github-pipelines/length9_78/training_17.csv",
    "Source9_78_18": "autopipeline-benchmarks/github-pipelines/length9_78/training_18.csv",
    "Source9_78_19": "autopipeline-benchmarks/github-pipelines/length9_78/training_19.csv",
    "Source9_78_20": "autopipeline-benchmarks/github-pipelines/length9_78/training_20.csv",
    "Source9_78_21": "autopipeline-benchmarks/github-pipelines/length9_78/training_21.csv",
    "Source9_78_22": "autopipeline-benchmarks/github-pipelines/length9_78/training_22.csv",
    "Source9_78_23": "autopipeline-benchmarks/github-pipelines/length9_78/training_23.csv",
    "Source9_78_24": "autopipeline-benchmarks/github-pipelines/length9_78/training_24.csv",
    "Source9_78_25": "autopipeline-benchmarks/github-pipelines/length9_78/training_25.csv",
    "Source9_78_26": "autopipeline-benchmarks/github-pipelines/length9_78/training_26.csv",
    "Source9_78_27": "autopipeline-benchmarks/github-pipelines/length9_78/training_27.csv",
    "Source9_78_28": "autopipeline-benchmarks/github-pipelines/length9_78/training_28.csv",
    "Source9_78_29": "autopipeline-benchmarks/github-pipelines/length9_78/training_29.csv",
    "Source9_78_30": "autopipeline-benchmarks/github-pipelines/length9_78/training_30.csv",
    "Source9_78_31": "autopipeline-benchmarks/github-pipelines/length9_78/training_31.csv",
    "Source9_78_32": "autopipeline-benchmarks/github-pipelines/length9_78/training_32.csv",
    "Source9_78_33": "autopipeline-benchmarks/github-pipelines/length9_78/training_33.csv",
    "Source9_78_34": "autopipeline-benchmarks/github-pipelines/length9_78/training_34.csv",
    "Source9_78_35": "autopipeline-benchmarks/github-pipelines/length9_78/training_35.csv",
    "Source9_78_36": "autopipeline-benchmarks/github-pipelines/length9_78/training_36.csv",
    "Source9_78_37": "autopipeline-benchmarks/github-pipelines/length9_78/training_37.csv",
    "Source9_78_38": "autopipeline-benchmarks/github-pipelines/length9_78/training_38.csv",
    "Source9_78_39": "autopipeline-benchmarks/github-pipelines/length9_78/training_39.csv",
    "Source9_78_40": "autopipeline-benchmarks/github-pipelines/length9_78/training_40.csv",
    "Source9_78_41": "autopipeline-benchmarks/github-pipelines/length9_78/training_41.csv",
    "Source9_78_42": "autopipeline-benchmarks/github-pipelines/length9_78/training_42.csv",
    "Source9_78_43": "autopipeline-benchmarks/github-pipelines/length9_78/training_43.csv",
    "Source9_78_44": "autopipeline-benchmarks/github-pipelines/length9_78/training_44.csv",
    "Source9_78_45": "autopipeline-benchmarks/github-pipelines/length9_78/training_45.csv",
    "Source9_78_46": "autopipeline-benchmarks/github-pipelines/length9_78/training_46.csv",
    "Source9_78_47": "autopipeline-benchmarks/github-pipelines/length9_78/training_47.csv",
    "Source9_78_48": "autopipeline-benchmarks/github-pipelines/length9_78/training_48.csv",
    "Source9_78_49": "autopipeline-benchmarks/github-pipelines/length9_78/training_49.csv",
    "Source9_78_50": "autopipeline-benchmarks/github-pipelines/length9_78/training_50.csv",
    "Source9_78_51": "autopipeline-benchmarks/github-pipelines/length9_78/training_51.csv",
    "Source9_78_52": "autopipeline-benchmarks/github-pipelines/length9_78/training_52.csv",
    "Source9_78_53": "autopipeline-benchmarks/github-pipelines/length9_78/training_53.csv",
    "Source9_78_54": "autopipeline-benchmarks/github-pipelines/length9_78/training_54.csv",
    "Source9_78_55": "autopipeline-benchmarks/github-pipelines/length9_78/training_55.csv",
    "Source9_78_56": "autopipeline-benchmarks/github-pipelines/length9_78/training_56.csv",
}

# Read all source tables into a list of dataframes
dfs = []
for name, path in source_files.items():
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

# UNION all source tables (concatenate rows)
result = pd.concat(dfs, ignore_index=True)

# Write the final output with exact column names as target schema
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_78/target_multisource_mcts.csv", index=False)