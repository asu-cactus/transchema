import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_3.csv", index_col=0)

join_1 = pd.merge(s1, s2, left_on=['x','y'], right_on=['x','y'], suffixes=('_1','_2'))
join_0 = pd.merge(s0, s2, left_on=['x','y'], right_on=['x','y'], suffixes=('_0','_2'))

join_1 = join_1[['x','y','label_1']].rename(columns={'label_1':'label'})
join_0 = join_0[['x','y','label_0']].rename(columns={'label_0':'label'})

union_all = pd.concat([s3, join_1, join_0], ignore_index=True)

def convert_label(lbl):
    try:
        return int(lbl)
    except:
        return {'purple':1, 'b':1, 'g':1, 'r':1}.get(lbl, 1)

union_all['label'] = union_all['label'].map(convert_label).astype(int)
union_all['y'] = union_all['y'].astype(int)
union_all['x'] = union_all['x'].astype(float)

result = union_all.groupby('y', as_index=False).agg({'x':'first', 'label':'first'})

result = result[['x','y','label']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts.csv", index=False)