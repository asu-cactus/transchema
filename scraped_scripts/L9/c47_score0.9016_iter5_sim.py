import pandas as pd

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
    "autopipeline-benchmarks/github-pipelines/length9_47/training_14.csv",
]

df0 = pd.read_csv(paths[0], index_col=0)
df12 = pd.read_csv(paths[12], index_col=0)

joined = pd.concat([df0, df12], axis=1, keys=['Source9_47_0', 'Source9_47_12'])
joined.columns = ['Source9_47_0.int_rate', 'Source9_47_12.int_rate']

unpivoted = joined.melt(value_vars=['Source9_47_0.int_rate', 'Source9_47_12.int_rate'], value_name='int_rate')
unpivoted = unpivoted[['int_rate']]

other_dfs = []
for i in range(1, 15):
    if i == 12:
        continue
    df = pd.read_csv(paths[i], index_col=0)
    other_dfs.append(df)

all_data = pd.concat(other_dfs + [unpivoted], ignore_index=True)
all_data['int_rate'] = all_data['int_rate'].astype('Int64')

all_data.to_csv("autopipeline-benchmarks/github-pipelines/length9_47/target_multisource_mcts.csv", index=False)