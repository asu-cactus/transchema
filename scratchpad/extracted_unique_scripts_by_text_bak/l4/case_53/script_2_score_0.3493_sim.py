import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

join_cols = ['WarID', 'PolityID']
join_result = pd.merge(s2, s0, on=join_cols, how='inner', suffixes=('_s2', '_s0'))

union_1_3 = pd.concat([s1, s3], ignore_index=True)

final_df = pd.concat([join_result, union_1_3], ignore_index=True)

cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

final_df = final_df[cols]

final_df['WarID'] = final_df['WarID'].astype('Int64')
final_df['PolityID'] = final_df['PolityID'].astype('Int64')
final_df['StartYear'] = final_df['StartYear'].astype('Int64')
final_df['StartMonth'] = final_df['StartMonth'].astype('Int64')
final_df['StartDay'] = final_df['StartDay'].astype('Int64')
final_df['EndYear'] = final_df['EndYear'].astype('Int64')
final_df['EndMonth'] = final_df['EndMonth'].astype('Int64')
final_df['EndDay'] = final_df['EndDay'].astype('Int64')
final_df['Side'] = final_df['Side'].map({'A':1, 'B':2}).astype('Int64')
final_df['IsInitiator'] = final_df['IsInitiator'].astype('Int64')
final_df['Outcome'] = final_df['Outcome'].astype('Int64')
final_df['Deaths'] = final_df['Deaths'].astype('Int64')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)