import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv", index_col=0)

join_cols = ['ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID']
join_result = pd.merge(s0, s2, on=join_cols, suffixes=('_0', '_2'))

union_0_1_3 = pd.concat([s0, s1, s3], ignore_index=True)

join_result = join_result[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE_0', 'INCIDENT_COUNT_0', 'SCHOOL_ID']]
join_result.columns = ['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']

combined = pd.concat([union_0_1_3, join_result], ignore_index=True)

combined['SCHOOL_YEAR'] = combined['SCHOOL_YEAR'].astype(str)
combined['ULCS_NO'] = combined['ULCS_NO'].astype(int)
combined['INCIDENT_TYPE'] = combined['INCIDENT_TYPE'].astype(str)
combined['INCIDENT_COUNT'] = combined['INCIDENT_COUNT'].fillna(0).astype(int)
combined['SCHOOL_ID'] = combined['SCHOOL_ID'].astype(int)

combined.to_csv("autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv", index=False)