import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str).str.extract(r'(\d{4})').astype(int)

pivoted = df_all.pivot_table(index=['ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID'], 
                             columns='INCIDENT_TYPE', 
                             values='INCIDENT_COUNT', 
                             aggfunc='sum', 
                             fill_value=0).reset_index()

melted = pivoted.melt(id_vars=['ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID'], 
                      var_name='INCIDENT_TYPE', 
                      value_name='INCIDENT_COUNT')

incident_type_map = {k: i+1 for i, k in enumerate(sorted(melted['INCIDENT_TYPE'].unique()))}
melted['INCIDENT_TYPE'] = melted['INCIDENT_TYPE'].map(incident_type_map)

melted = melted[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

melted = melted.astype({'ULCS_NO': int, 'SCHOOL_YEAR': int, 'INCIDENT_TYPE': int, 'INCIDENT_COUNT': int, 'SCHOOL_ID': int})

melted.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)