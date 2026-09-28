import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_49/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_49/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_49/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_49/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_49/training_4.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

df_all['Sex'] = df_all['Sex'].astype(str).str.strip()
sex_map = {'Female': 8, 'Male': 11, 'Refused': 8}
df_all['Sex'] = df_all['Sex'].map(sex_map).fillna(df_all['Sex']).astype(int)

agg_df = df_all.groupby(['Age Group', 'Sex'], as_index=False).agg({
    "Don't know/Refused/Missing": 'sum',
    'Normal Weight': 'sum',
    'Obese': 'sum',
    'Overweight': 'sum',
    'Underweight': 'sum'
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_49/target_multisource_mcts.csv", index=False)