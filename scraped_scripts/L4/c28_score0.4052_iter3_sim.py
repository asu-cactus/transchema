import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

grouped_0 = df0.groupby(['INCIDENT_TYPE', 'SCHOOL_YEAR', 'ULCS_NO', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()
grouped_1 = df1.groupby(['INCIDENT_TYPE', 'SCHOOL_YEAR', 'ULCS_NO', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()
grouped_2 = df2.groupby(['INCIDENT_TYPE', 'SCHOOL_YEAR', 'ULCS_NO', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()
grouped_3 = df3.groupby(['INCIDENT_TYPE', 'SCHOOL_YEAR', 'ULCS_NO', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

union_df = pd.concat([grouped_0, grouped_1, grouped_2, grouped_3], ignore_index=True)

final_df = union_df.groupby(['INCIDENT_TYPE', 'SCHOOL_YEAR', 'ULCS_NO', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

final_df['ULCS_NO'] = final_df['ULCS_NO'].astype(int)
final_df['SCHOOL_YEAR'] = final_df['SCHOOL_YEAR'].astype(str)
final_df['SCHOOL_ID'] = final_df['SCHOOL_ID'].astype(int)
final_df['INCIDENT_COUNT'] = final_df['INCIDENT_COUNT'].astype(int)
final_df['INCIDENT_TYPE'] = final_df['INCIDENT_TYPE'].astype(str)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)