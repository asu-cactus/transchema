import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

all_sources = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Convert 'y' to float
all_sources['y'] = all_sources['y'].astype(float)

# Convert 'x' to integer
all_sources['x'] = all_sources['x'].astype(int)

# Convert 'label' to integer by factorizing (assign unique int per label)
all_sources['label'] = pd.factorize(all_sources['label'])[0].astype(int)

# Reorder columns to match target schema: ['y', 'x', 'label']
all_sources = all_sources[['y', 'x', 'label']]

all_sources.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)