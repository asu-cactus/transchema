import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

df1['grade_numeric'] = df1['grade'].str.extract('(\d+)').astype(float)

df1_unpivot = df1.melt(id_vars=['school_name', 'grade_numeric'], value_vars=['reading_score', 'math_score'], var_name='a', value_name='b')
df1_unpivot['a'] = df1_unpivot['a'].map({'reading_score': 'reading_score', 'math_score': 'math_score'})

agg = df1_unpivot.groupby(['school_name', 'a']).agg(
    b=('b', 'sum'),
    c=('grade_numeric', 'mean')
).reset_index()

df0_renamed = df0.rename(columns={'type': 'a', 'size': 'b', 'budget': 'c'})

df_merged = pd.merge(df0_renamed, agg, on=['school_name', 'a'], how='outer')

df_merged['d'] = df_merged['c_y'] / 25000
df_merged['e'] = df_merged['c_y'] / 23000

df_merged = df_merged.rename(columns={'b_x': 'b', 'c_x': 'c'})
df_merged = df_merged[['school_name', 'a', 'b', 'c', 'd', 'e']]

df_merged['a'] = df_merged['a'].replace({'reading_score': 'Charter', 'math_score': 'District'}).fillna(df_merged['a'])

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)