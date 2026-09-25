import pandas as pd

paths = {
    "Source9_47_0": "autopipeline-benchmarks/github-pipelines/length9_47/training_0.csv",
    "Source9_47_1": "autopipeline-benchmarks/github-pipelines/length9_47/training_1.csv",
    "Source9_47_2": "autopipeline-benchmarks/github-pipelines/length9_47/training_2.csv",
    "Source9_47_3": "autopipeline-benchmarks/github-pipelines/length9_47/training_3.csv",
    "Source9_47_4": "autopipeline-benchmarks/github-pipelines/length9_47/training_4.csv",
    "Source9_47_5": "autopipeline-benchmarks/github-pipelines/length9_47/training_5.csv",
    "Source9_47_6": "autopipeline-benchmarks/github-pipelines/length9_47/training_6.csv",
    "Source9_47_7": "autopipeline-benchmarks/github-pipelines/length9_47/training_7.csv",
    "Source9_47_8": "autopipeline-benchmarks/github-pipelines/length9_47/training_8.csv",
    "Source9_47_9": "autopipeline-benchmarks/github-pipelines/length9_47/training_9.csv",
    "Source9_47_10": "autopipeline-benchmarks/github-pipelines/length9_47/training_10.csv",
    "Source9_47_11": "autopipeline-benchmarks/github-pipelines/length9_47/training_11.csv",
    "Source9_47_12": "autopipeline-benchmarks/github-pipelines/length9_47/training_12.csv",
    "Source9_47_13": "autopipeline-benchmarks/github-pipelines/length9_47/training_13.csv",
    "Source9_47_14": "autopipeline-benchmarks/github-pipelines/length9_47/training_14.csv",
}

df0 = pd.read_csv(paths["Source9_47_0"], index_col=0)
df1 = pd.read_csv(paths["Source9_47_1"], index_col=0)
df2 = pd.read_csv(paths["Source9_47_2"], index_col=0)
df3 = pd.read_csv(paths["Source9_47_3"], index_col=0)
df4 = pd.read_csv(paths["Source9_47_4"], index_col=0)
df5 = pd.read_csv(paths["Source9_47_5"], index_col=0)
df6 = pd.read_csv(paths["Source9_47_6"], index_col=0)
df7 = pd.read_csv(paths["Source9_47_7"], index_col=0)
df8 = pd.read_csv(paths["Source9_47_8"], index_col=0)
df9 = pd.read_csv(paths["Source9_47_9"], index_col=0)
df10 = pd.read_csv(paths["Source9_47_10"], index_col=0)
df11 = pd.read_csv(paths["Source9_47_11"], index_col=0)
df12 = pd.read_csv(paths["Source9_47_12"], index_col=0)
df13 = pd.read_csv(paths["Source9_47_13"], index_col=0)
df14 = pd.read_csv(paths["Source9_47_14"], index_col=0)

joined = pd.merge(df1, df13, left_index=True, right_index=True, suffixes=('_1', '_13'))

unpivoted = joined.melt(value_vars=['int_rate_1', 'int_rate_13'], value_name='int_rate')[['int_rate']]

frames = [df0, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12, df14, unpivoted]

result = pd.concat(frames, ignore_index=True)

result['int_rate'] = result['int_rate'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_47/target_multisource_mcts.csv", index=False)