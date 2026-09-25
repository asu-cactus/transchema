import pandas as pd

sources = [
    "autopipeline-benchmarks/github-pipelines/length9_77/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_38.csv",
]

dfs = [pd.read_csv(path, index_col=0) for path in sources]

df = pd.concat(dfs, ignore_index=True)

df = df.astype({
    "anime_id": "Int64",
    "name": "string",
    "genre": "string",
    "type": "string",
    "episodes": "Int64",
    "rating": "float64",
    "members": "Int64"
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_77/target_multisource_mcts.csv", index=False)