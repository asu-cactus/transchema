import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_24/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_24/training_1.csv"
source2_path = "autopipeline-benchmarks/github-pipelines/length3_24/training_2.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_24/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)
df2 = pd.read_csv(source2_path, index_col=0)

merged = df2.merge(df0[['user_id', 'gender']], on='user_id', how='inner')
merged = merged.merge(df1[['movie_id', 'title']], on='movie_id', how='inner')

grouped = merged.groupby(['title', 'gender'], as_index=False)['rating'].mean()

pivoted = grouped.pivot(index='title', columns='gender', values='rating').reset_index()

pivoted.columns.name = None
pivoted = pivoted.rename(columns={'F': 'F', 'M': 'M'})

pivoted.to_csv(target_path, index=False)