import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_16/training_4.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

age_map = {
    "Age 18 to 24": 5,
    "Age 25 to 34": 5,
    "Age 35 to 44": 5,
    "Age 45 to 54": 5,
    "Age 55 to 64": 5,
    "Age 65 to 74": 5,
    "Age 75 or older": 5,
    "Refused": 5,
    "Don't know": 5,
    "Missing": 5
}
df_all['Age Group'] = df_all['Age Group'].map(age_map).fillna(5).astype(int)

sex_map = {
    "Female": 5,
    "Male": 5,
    "Refused": 5,
    "Don't know": 5,
    "Missing": 5
}
df_all['Sex'] = df_all['Sex'].map(sex_map).fillna(5).astype(int)

df_all["Don't know/Refused/Missing"] = pd.to_numeric(df_all["Don't know/Refused/Missing"], errors='coerce').fillna(0).astype(int)
df_all["Normal Weight"] = pd.to_numeric(df_all["Normal Weight"], errors='coerce').fillna(0).astype(int)
df_all["Obese"] = pd.to_numeric(df_all["Obese"], errors='coerce').fillna(0).astype(int)
df_all["Overweight"] = pd.to_numeric(df_all["Overweight"], errors='coerce').fillna(0).astype(int)
df_all["Underweight"] = pd.to_numeric(df_all["Underweight"], errors='coerce').fillna(0).astype(int)

df_all['index'] = df_all.index.astype(int)

grouped = df_all.groupby(['index', 'Age Group', 'Sex'], as_index=False).sum()

grouped = grouped[['index', 'Age Group', 'Sex', "Don't know/Refused/Missing", 'Normal Weight', 'Obese', 'Overweight', 'Underweight']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_16/target_multisource_mcts.csv", index=False)