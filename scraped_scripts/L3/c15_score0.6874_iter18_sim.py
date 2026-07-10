import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_2.csv", index_col=0)

joined_0_2 = pd.merge(source2, source0, how='inner', left_on='movie_id', right_on='movie_id')
joined_all = pd.merge(joined_0_2, source1, how='inner', left_on='user_id', right_on='user_id')

grouped = joined_all.groupby(['title', 'gender']).agg(count_user_id=('user_id', 'count')).reset_index()

pivoted = grouped.pivot(index='title', columns='gender', values='count_user_id').fillna(0)

pivoted = pivoted.rename(columns={'F': 'F', 'M': 'M'}).reset_index()

pivoted['F'] = pivoted['F'].astype(float)
pivoted['M'] = pivoted['M'].astype(float)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length3_15/target_multisource_mcts.csv", index=False)