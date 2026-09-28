import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

agg = df0.groupby(['Artist', 'Years Waited', '# of Years Nominated']).agg(
    count_distinct_artist=pd.NamedAgg(column='Artist', aggfunc=lambda x: x.nunique()),
    count_artist=pd.NamedAgg(column='Artist', aggfunc='count')
).reset_index()

join0 = pd.merge(agg, df0, on='Artist', how='left', suffixes=('_agg', '_src0'))

join1 = pd.merge(join0, df1, on='Artist', how='left')

join2 = pd.merge(join1, df2, on='Artist', how='left', suffixes=('', '_src2'))

join3 = pd.merge(join2, df3, on='Artist', how='left')

result = join3[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced', 'Certified Units (Millions)']]

result['Year Inducted'] = pd.to_numeric(result['Year Inducted'], errors='coerce')
result['Years Waited'] = pd.to_numeric(result['Years Waited'], errors='coerce').astype('Int64')
result['# of Years Nominated'] = pd.to_numeric(result['# of Years Nominated'], errors='coerce').astype('Int64')
result['Certified Units (Millions)'] = pd.to_numeric(result['Certified Units (Millions)'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)