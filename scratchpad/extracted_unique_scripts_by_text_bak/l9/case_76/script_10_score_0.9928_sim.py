import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_76/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_38.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
df_grouped = df_all.groupby("genre", as_index=False)["members"].sum()
df_grouped["genre"] = df_grouped["genre"].astype(str)
df_grouped["members"] = df_grouped["members"].astype(int)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_76/target_multisource_mcts.csv", index=False)