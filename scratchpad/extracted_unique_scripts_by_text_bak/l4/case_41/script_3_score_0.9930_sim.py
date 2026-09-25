import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

joined_0_1 = pd.merge(s0, s1, left_on=['x', 'y'], right_on=['x', 'y'], suffixes=('_0', '_1'))

all_sources = pd.concat([s0, s1, s2, s3], ignore_index=True)

all_sources['y'] = all_sources['y'].astype(float)
all_sources['x'] = all_sources['x'].astype(int)

def label_to_int(label):
    try:
        return int(label)
    except:
        return 1

all_sources['label'] = all_sources['label'].apply(label_to_int).astype(int)

all_sources = all_sources[['y', 'x', 'label']]

all_sources.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)