import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_18/training_0.csv", index_col=0)

df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce').fillna(0)
df0['distance_of_shot'] = pd.to_numeric(df0['distance_of_shot'], errors='coerce').fillna(0)

agg = df0.groupby('area_of_shot').agg(
    area_shot_sum=pd.NamedAgg(column='distance_of_shot', aggfunc='sum'),
    is_goal_count=pd.NamedAgg(column='is_goal', aggfunc='sum'),
    count_shot_id=pd.NamedAgg(column='shot_id_number', aggfunc='count')
).reset_index()

agg['is_goal'] = 0.0

agg = agg.rename(columns={'area_of_shot': 'area_of_shot'})

agg = agg[['area_of_shot', 'is_goal', 'area_shot_sum', 'is_goal_count']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_18/target_multisource_mcts.csv", index=False)