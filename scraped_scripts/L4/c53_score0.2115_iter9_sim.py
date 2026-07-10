import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

join_cols = ['WarID', 'PolityID', 'Side', 'IsInitiator', 'Outcome']

join_result = pd.merge(s2, s0, on=join_cols, suffixes=('_s2', '_s0'))

join_result['PolityName'] = join_result['PolityName']

join_result = join_result[['PolityName', 'WarID', 'PolityID', 'StartYear_s2', 'StartMonth_s2', 'StartDay_s2',
                           'EndYear_s2', 'EndMonth_s2', 'EndDay_s2', 'Side', 'IsInitiator', 'Outcome', 'Deaths_s2']]

join_result.columns = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                       'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

union_013 = pd.concat([s0, s1, s3], ignore_index=True, sort=False)

final_df = pd.concat([join_result, union_013], ignore_index=True, sort=False)

final_df = final_df[['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                     'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]

final_df['PolityName'] = final_df['PolityName'].astype(str)
final_df['WarID'] = pd.to_numeric(final_df['WarID'], errors='coerce').astype('Int64')
final_df['PolityID'] = pd.to_numeric(final_df['PolityID'], errors='coerce').astype('Int64')
final_df['StartYear'] = pd.to_numeric(final_df['StartYear'], errors='coerce').astype('Int64')
final_df['StartMonth'] = pd.to_numeric(final_df['StartMonth'], errors='coerce').astype('Int64')
final_df['StartDay'] = pd.to_numeric(final_df['StartDay'], errors='coerce').astype('Int64')
final_df['EndYear'] = pd.to_numeric(final_df['EndYear'], errors='coerce').astype('Int64')
final_df['EndMonth'] = pd.to_numeric(final_df['EndMonth'], errors='coerce').astype('Int64')
final_df['EndDay'] = pd.to_numeric(final_df['EndDay'], errors='coerce').astype('Int64')
final_df['Side'] = pd.to_numeric(final_df['Side'], errors='coerce').astype('Int64')
final_df['IsInitiator'] = pd.to_numeric(final_df['IsInitiator'], errors='coerce').astype('Int64')
final_df['Outcome'] = pd.to_numeric(final_df['Outcome'], errors='coerce').astype('Int64')
final_df['Deaths'] = pd.to_numeric(final_df['Deaths'], errors='coerce').fillna(0).astype('Int64')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)