import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

s0 = s0.rename(columns={'y': 'y_0', 'label': 'label_0'})
s1 = s1.rename(columns={'y': 'y_1', 'label': 'label_1'})
s2 = s2.rename(columns={'y': 'y_2', 'label': 'label_2'})
s3 = s3.rename(columns={'y': 'y_3', 'label': 'label_3'})

df = s0.merge(s1, on='x', how='inner').merge(s2, on='x', how='inner').merge(s3, on='x', how='inner')

rows = []
for i in range(4):
    rows.append(pd.DataFrame({
        'x': df['x'],
        'y': df[f'y_{i}'],
        'label': df[f'label_{i}']
    }))

result = pd.concat(rows, ignore_index=True)

def label_to_int(label):
    try:
        return int(label)
    except:
        return {'g':1, 'r':1, 'purple':1, 'b':1}.get(label, None)

result['label'] = result['label'].map(label_to_int).astype('Int64')
result['x'] = result['x'].astype(int)
result['y'] = result['y'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)