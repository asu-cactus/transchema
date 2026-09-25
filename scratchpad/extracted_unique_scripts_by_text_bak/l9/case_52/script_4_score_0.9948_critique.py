import pandas as pd

paths = {
    "Source9_52_0": "autopipeline-benchmarks/github-pipelines/length9_52/training_0.csv",
    "Source9_52_1": "autopipeline-benchmarks/github-pipelines/length9_52/training_1.csv",
    "Source9_52_2": "autopipeline-benchmarks/github-pipelines/length9_52/training_2.csv",
    "Source9_52_3": "autopipeline-benchmarks/github-pipelines/length9_52/training_3.csv",
    "Source9_52_4": "autopipeline-benchmarks/github-pipelines/length9_52/training_4.csv",
    "Source9_52_5": "autopipeline-benchmarks/github-pipelines/length9_52/training_5.csv",
    "Source9_52_6": "autopipeline-benchmarks/github-pipelines/length9_52/training_6.csv",
    "Source9_52_7": "autopipeline-benchmarks/github-pipelines/length9_52/training_7.csv",
    "Source9_52_8": "autopipeline-benchmarks/github-pipelines/length9_52/training_8.csv",
    "Source9_52_9": "autopipeline-benchmarks/github-pipelines/length9_52/training_9.csv",
    "Source9_52_10": "autopipeline-benchmarks/github-pipelines/length9_52/training_10.csv",
    "Source9_52_11": "autopipeline-benchmarks/github-pipelines/length9_52/training_11.csv",
    "Source9_52_12": "autopipeline-benchmarks/github-pipelines/length9_52/training_12.csv",
    "Source9_52_13": "autopipeline-benchmarks/github-pipelines/length9_52/training_13.csv",
    "Source9_52_14": "autopipeline-benchmarks/github-pipelines/length9_52/training_14.csv",
}

source_names = [
    "Source9_52_0", "Source9_52_1", "Source9_52_2", "Source9_52_3", "Source9_52_4",
    "Source9_52_5", "Source9_52_6", "Source9_52_7", "Source9_52_8", "Source9_52_9",
    "Source9_52_10", "Source9_52_11", "Source9_52_12", "Source9_52_13", "Source9_52_14"
]

dfs = [pd.read_csv(paths[src], index_col=0) for src in source_names]

result = pd.concat(dfs, ignore_index=True)

result = result.astype({"zip_code": "int64"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_52/target_multisource_mcts.csv", index=False)