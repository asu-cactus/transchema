import pandas as pd

paths = {
    "Source9_49_0": "autopipeline-benchmarks/github-pipelines/length9_49/training_0.csv",
    "Source9_49_1": "autopipeline-benchmarks/github-pipelines/length9_49/training_1.csv",
    "Source9_49_2": "autopipeline-benchmarks/github-pipelines/length9_49/training_2.csv",
    "Source9_49_3": "autopipeline-benchmarks/github-pipelines/length9_49/training_3.csv",
    "Source9_49_4": "autopipeline-benchmarks/github-pipelines/length9_49/training_4.csv",
    "Source9_49_5": "autopipeline-benchmarks/github-pipelines/length9_49/training_5.csv",
    "Source9_49_6": "autopipeline-benchmarks/github-pipelines/length9_49/training_6.csv",
    "Source9_49_7": "autopipeline-benchmarks/github-pipelines/length9_49/training_7.csv",
    "Source9_49_8": "autopipeline-benchmarks/github-pipelines/length9_49/training_8.csv",
    "Source9_49_9": "autopipeline-benchmarks/github-pipelines/length9_49/training_9.csv",
    "Source9_49_10": "autopipeline-benchmarks/github-pipelines/length9_49/training_10.csv",
    "Source9_49_11": "autopipeline-benchmarks/github-pipelines/length9_49/training_11.csv",
    "Source9_49_12": "autopipeline-benchmarks/github-pipelines/length9_49/training_12.csv",
    "Source9_49_13": "autopipeline-benchmarks/github-pipelines/length9_49/training_13.csv",
    "Source9_49_14": "autopipeline-benchmarks/github-pipelines/length9_49/training_14.csv",
}

df_4 = pd.read_csv(paths["Source9_49_4"], index_col=0)
df_5 = pd.read_csv(paths["Source9_49_5"], index_col=0)

joined = pd.merge(df_4, df_5, left_on="emp_title", right_on="emp_title", how="inner", suffixes=('_4', '_5'))

unpivot_rows = []
for col in joined.columns:
    if col.startswith("emp_title"):
        unpivot_rows.append(joined[[col]].rename(columns={col: "emp_title"}))
unpivot_result = pd.concat(unpivot_rows, ignore_index=True)

sources_to_union = [
    "Source9_49_0", "Source9_49_1", "Source9_49_2", "Source9_49_3",
    "Source9_49_6", "Source9_49_7", "Source9_49_8", "Source9_49_9",
    "Source9_49_10", "Source9_49_11", "Source9_49_12", "Source9_49_13",
    "Source9_49_14"
]

dfs = [pd.read_csv(paths[src], index_col=0) for src in sources_to_union]
dfs.append(unpivot_result)

final_df = pd.concat(dfs, ignore_index=True)
final_df = final_df[["emp_title"]]
final_df["emp_title"] = final_df["emp_title"].astype(int)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_49/target_multisource_mcts.csv", index=False)