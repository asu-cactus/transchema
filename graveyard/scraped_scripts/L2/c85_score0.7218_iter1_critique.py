import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_85/training_1.csv", index_col=0)

# Extract numeric part of Mouse ID in both tables to ensure matching keys
df0_mouse_id_num = df0['Mouse ID'].str.extract('(\d+)').astype(int)
df0 = df0.assign(Mouse_ID_num=df0_mouse_id_num)

df1_mouse_id_num = df1['Mouse ID'].str.extract('(\d+)').astype(int)
df1 = df1.assign(Mouse_ID_num=df1_mouse_id_num)

# Join on numeric Mouse ID
df_joined = pd.merge(df0, df1, left_on='Mouse_ID_num', right_on='Mouse_ID_num', how='inner')

# Group by Drug and Timepoint, aggregate count distinct Mouse ID (numeric)
result = df_joined.groupby(['Drug', 'Timepoint'], as_index=False).agg({'Mouse_ID_num': 'nunique'})

# Rename columns to match target schema
result = result.rename(columns={'Mouse_ID_num': 'Mouse ID'})

# Ensure types
result['Drug'] = result['Drug'].astype(str)
result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_85/target_multisource_mcts.csv", index=False)