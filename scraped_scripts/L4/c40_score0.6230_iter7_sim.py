import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_3.csv", index_col=0)

joined = pd.merge(s1, s2, left_on=['x','y'], right_on=['x','y'], suffixes=('_1','_2'))

unpivot_rows = []
for idx, row in joined.iterrows():
    unpivot_rows.append({'x': row['x'], 'y': row['y'], 'label': row['label_1']})
    unpivot_rows.append({'x': row['x'], 'y': row['y'], 'label': row['label_2']})
unpivot_result = pd.DataFrame(unpivot_rows)

combined = pd.concat([s0, s3, unpivot_result], ignore_index=True)

combined['x'] = combined['x'].astype(float)
combined['y'] = combined['y'].astype(int)
combined['label'] = combined['label'].astype('category').cat.codes.astype(int)

combined.to_csv("autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts.csv", index=False)