import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['Year'] = df_all.groupby('Wrestler').cumcount() + 2013

df_melted = df_all.melt(id_vars=['Wrestler', 'Year'], value_vars=['Wins', 'Losses', 'Draws'], var_name='Result', value_name='Count')

df_melted['Year_Result'] = df_melted['Year'].astype(str) + ' ' + df_melted['Result']

df_pivot = df_melted.pivot_table(index='Wrestler', columns='Year_Result', values='Count', aggfunc='sum')

df_pivot.columns.name = None
df_pivot = df_pivot.reset_index()

expected_cols = ['Wrestler',
 '2013 Wins', '2013 Losses', '2013 Draws',
 '2014 Wins', '2014 Losses', '2014 Draws',
 '2015 Wins', '2015 Losses', '2015 Draws',
 '2016 Wins', '2016 Losses', '2016 Draws']

for col in expected_cols[1:]:
    if col not in df_pivot.columns:
        df_pivot[col] = 0

df_final = df_pivot[expected_cols]

int_cols = expected_cols[1:]
df_final[int_cols] = df_final[int_cols].fillna(0).astype(int)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_8/target_multisource_mcts.csv", index=False)