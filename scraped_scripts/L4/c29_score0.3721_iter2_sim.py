import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].str.extract(r'(\d{4})').astype(int)

df_pivot = df_all.pivot_table(index=['ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID'], 
                              columns='INCIDENT_TYPE', 
                              values='INCIDENT_COUNT', 
                              aggfunc='sum', 
                              fill_value=0).reset_index()

incident_cols = [col for col in df_pivot.columns if col not in ['ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID']]

df_melted = df_pivot.melt(id_vars=['ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID'], 
                          value_vars=incident_cols, 
                          var_name='INCIDENT_TYPE', 
                          value_name='INCIDENT_COUNT')

df_melted['INCIDENT_TYPE'] = df_melted['INCIDENT_TYPE'].str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)

incident_type_map = {v: k+1 for k, v in enumerate(sorted(df_melted['INCIDENT_TYPE'].unique()))}
df_melted['INCIDENT_TYPE'] = df_melted['INCIDENT_TYPE'].map(incident_type_map)

df_melted = df_melted.astype({'ULCS_NO': int, 'SCHOOL_YEAR': int, 'INCIDENT_TYPE': int, 'INCIDENT_COUNT': int, 'SCHOOL_ID': int})

df_melted.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)