import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_1.csv", index_col=0)

agg1 = df1.groupby('city').agg(min_fare=('fare', 'min'), max_fare=('fare', 'max')).reset_index()

merged = pd.merge(df0, agg1, on='city', how='inner')

agg2 = merged.groupby(['city', 'type']).agg(fare=('min_fare', 'mean'), max_fare=('max_fare', 'mean')).reset_index()

agg2['fare'] = agg2[['fare', 'max_fare']].mean(axis=1)
agg2 = agg2.drop(columns=['max_fare'])

agg2.to_csv("autopipeline-benchmarks/github-pipelines/length3_69/target_multisource_mcts.csv", index=False)