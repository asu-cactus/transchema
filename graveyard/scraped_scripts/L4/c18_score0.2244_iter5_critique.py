import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_18/training_0.csv", index_col=0)

df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce').fillna(0)
df0['distance_of_shot'] = pd.to_numeric(df0['distance_of_shot'], errors='coerce').fillna(0)

agg = df0.groupby('area_of_shot').agg(
    is_goal_count=pd.NamedAgg(column='is_goal', aggfunc='sum'),
    area_shot_sum=pd.NamedAgg(column='distance_of_shot', aggfunc='sum'),
    count_shot_id=pd.NamedAgg(column='shot_id_number', aggfunc='count')
).reset_index()

# The target schema is ['area_of_shot': string, 'is_goal': float, 'area_shot_sum': integer, 'is_goal_count': integer]
# The 'is_goal' column in target examples is float but seems to be a flag or average. Since target examples have NaN and 0/1,
# we can set 'is_goal' as NaN (or 0) because it is not aggregated in source. The original script set it to 0.0.
# But better to set it as NaN to match target examples with NaN.

agg['is_goal'] = float('nan')

# Reorder columns to match target schema
agg = agg[['area_of_shot', 'is_goal', 'area_shot_sum', 'is_goal_count']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_18/target_multisource_mcts.csv", index=False)