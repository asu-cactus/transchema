import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_16/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_16/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_16/training_2.csv', index_col=0)

df01 = pd.merge(source1, source0[['user_id', 'gender']], on='user_id', how='inner')
df012 = pd.merge(df01, source2[['movie_id', 'title']], on='movie_id', how='inner')

f_avg = df012[df012['gender'] == 'F'].groupby('title')['rating'].mean()
m_avg = df012[df012['gender'] == 'M'].groupby('title')['rating'].mean()

result = pd.DataFrame({'title': f_avg.index})
result['F'] = f_avg.values
result['M'] = m_avg.reindex(result['title']).values

result.to_csv('autopipeline-benchmarks/github-pipelines/length3_16/target_multisource_mcts.csv', index=False)