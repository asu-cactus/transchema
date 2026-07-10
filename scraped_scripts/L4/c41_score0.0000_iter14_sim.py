import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

s0 = s0.rename(columns={'x':'x_0', 'y':'y_0', 'label':'label_0'})
s1 = s1.rename(columns={'x':'x_1', 'y':'y_1', 'label':'label_1'})
s2 = s2.rename(columns={'x':'x_2', 'y':'y_2', 'label':'label_2'})
s3 = s3.rename(columns={'x':'x_3', 'y':'y_3', 'label':'label_3'})

join_0_1 = pd.merge(s0, s1, left_on='label_0', right_on='label_1', how='inner')
join_0_1_2 = pd.merge(join_0_1, s2, left_on='label_0', right_on='label_2', how='inner')
join_0_1_2_3 = pd.merge(join_0_1_2, s3, left_on='label_0', right_on='label_3', how='inner')

grouped = join_0_1_2_3.groupby('label_0').agg({
    'y_0':'mean', 'y_1':'mean', 'y_2':'mean', 'y_3':'mean',
    'x_0':'mean', 'x_1':'mean', 'x_2':'mean', 'x_3':'mean'
}).reset_index()

grouped['y'] = grouped[['y_0','y_1','y_2','y_3']].mean(axis=1)
grouped['x'] = grouped[['x_0','x_1','x_2','x_3']].mean(axis=1).round().astype(int)
grouped['label'] = grouped['label_0'].astype('category').cat.codes

result = grouped[['y','x','label']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)