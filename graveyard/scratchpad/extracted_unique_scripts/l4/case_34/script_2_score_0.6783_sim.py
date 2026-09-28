import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_4.csv", index_col=0)

grouped_source0 = source0.groupby('batsman', as_index=False).agg({'batsman_runs':'sum'}).rename(columns={'batsman_runs':'batsman_runs_x'})
grouped_source3 = source3.groupby('batsman', as_index=False).agg({'batsman_runs':'sum'}).rename(columns={'batsman_runs':'batsman_runs_y'})

joined_0_3 = pd.merge(grouped_source0, grouped_source3, on='batsman', how='outer')

joined_0_3_1 = pd.merge(joined_0_3, source1, on='batsman', how='outer').rename(columns={'total_runs':'total_runs_x'})

joined_0_3_1_4 = pd.merge(joined_0_3_1, source4, on='batsman', how='outer').rename(columns={'total_runs':'total_runs_y'})

final_join = pd.merge(joined_0_3_1_4, source2, on='batsman', how='outer')

final_join['batsman_runs'] = final_join['batsman_runs_x'].fillna(0) + final_join['batsman_runs_y'].fillna(0)
final_join['no of balls'] = final_join['no of balls'].fillna(0).astype(int)
final_join['strike'] = final_join['strike'].astype(float)
final_join['total_runs_x'] = final_join['total_runs_x'].fillna(0).astype(int)
final_join['total_runs_y'] = final_join['total_runs_y'].fillna(0).astype(int)
final_join['batsman_runs_x'] = final_join['batsman_runs_x'].fillna(0).astype(int)
final_join['batsman_runs_y'] = final_join['batsman_runs_y'].fillna(0).astype(int)
final_join['batsman_runs'] = final_join['batsman_runs'].astype(int)

final = final_join[['batsman', 'total_runs_x', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs', 'strike', 'total_runs_y']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_34/target_multisource_mcts.csv", index=False)