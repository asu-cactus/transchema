import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_3.csv", index_col=0)

join_result = pd.merge(s1, s2, how='inner', left_on=['x','y'], right_on=['x','y'], suffixes=('_1','_2'))

def label_to_int(label_series):
    unique_labels = pd.Series(label_series.unique()).dropna().reset_index(drop=True)
    mapping = {label: idx+1 for idx, label in unique_labels.items()}
    return label_series.map(mapping)

s0['label'] = label_to_int(s0['label'])
s3['label'] = label_to_int(s3['label'])
join_result['label_1'] = label_to_int(join_result['label_1'])
join_result['label_2'] = label_to_int(join_result['label_2'])

join_result['label'] = join_result['label_1'].combine_first(join_result['label_2'])
join_result = join_result[['x','y','label']]

combined = pd.concat([s0, s3, join_result], ignore_index=True)

combined['x'] = combined['x'].astype(float)
combined['y'] = combined['y'].astype(int)
combined['label'] = combined['label'].astype(int)

combined.to_csv("autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts.csv", index=False)