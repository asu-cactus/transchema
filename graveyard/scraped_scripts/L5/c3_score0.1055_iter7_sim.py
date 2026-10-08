import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_5.csv", index_col=0)

s1['Top 100 Singles'] = pd.to_numeric(s1['Top 100 Singles'], errors='coerce')
s1['Highest Position'] = pd.to_numeric(s1['Highest Position'], errors='coerce')
s5['Years Waited'] = pd.to_numeric(s5['Years Waited'], errors='coerce')
s5['# of Years Nominated'] = pd.to_numeric(s5['# of Years Nominated'], errors='coerce')
s5['Year Inducted'] = pd.to_numeric(s5['Year Inducted'], errors='coerce')

agg = s1.groupby(['Artist', 'Top 100 Singles', 'Highest Position']).agg(
    Artist_count=('Artist', 'count')
).reset_index()

agg2 = s2.groupby('Artist').agg({'Certified Units (Millions)': 'sum'}).reset_index()
agg4 = s4.groupby('Artist').agg({'Influenced': 'sum'}).reset_index()
agg0 = s0.groupby('Artist').agg({'Albums in RS500': 'sum'}).reset_index()

agg = agg.merge(agg2, on='Artist', how='left')
agg = agg.merge(agg4, on='Artist', how='left')
agg = agg.merge(agg0, on='Artist', how='left')

agg = agg.merge(s5[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By']], on='Artist', how='left')

result = agg[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced', 'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position']]

result['Years Waited'] = pd.to_numeric(result['Years Waited'], errors='coerce').astype('Int64')
result['# of Years Nominated'] = pd.to_numeric(result['# of Years Nominated'], errors='coerce').astype('Int64')
result['Influenced'] = pd.to_numeric(result['Influenced'], errors='coerce').astype('Int64')
result['Albums in RS500'] = pd.to_numeric(result['Albums in RS500'], errors='coerce').astype('Int64')
result['Top 100 Singles'] = pd.to_numeric(result['Top 100 Singles'], errors='coerce').astype('Int64')
result['Highest Position'] = pd.to_numeric(result['Highest Position'], errors='coerce').astype('Int64')
result['Certified Units (Millions)'] = pd.to_numeric(result['Certified Units (Millions)'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_3/target_multisource_mcts.csv", index=False)