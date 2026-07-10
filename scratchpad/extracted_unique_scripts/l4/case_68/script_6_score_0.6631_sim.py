import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

df0_unpivot = pd.melt(df0, id_vars=['school_name', 'type'], value_vars=['size', 'budget'], var_name='a', value_name='b')
df0_unpivot['a'] = df0_unpivot['type'].astype(str) + ' ' + df0_unpivot['a']
df0_unpivot = df0_unpivot.drop(columns=['type'])

df0_agg = df0_unpivot.groupby(['school_name', 'a'], as_index=False)['b'].sum()

df1_agg = df1.groupby(['school_name'], as_index=False).agg({'reading_score':'sum', 'math_score':'sum'})

df_join = pd.merge(df0_agg, df1_agg, on='school_name', how='inner')

df_join = df_join.rename(columns={'reading_score':'c', 'math_score':'d'})

df_join['b'] = df_join['b'].astype(int)
df_join['c'] = df_join['c'].astype(int)
df_join['d'] = df_join['d'].astype(float)

df_join['e'] = df_join['d']  # e is same as d in target examples

df_join = df_join[['school_name', 'a', 'b', 'c', 'd', 'e']]

df_join.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)