import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

df_pivot1 = df0.pivot(index='PassengerId', columns='Embarked', values='Fare')
df_pivot1.columns = [f'Fare_{col}' for col in df_pivot1.columns]

df_pivot2 = df0.pivot(index='PassengerId', columns='Pclass', values='Fare')
df_pivot2.columns = [f'Fare_{col}' for col in df_pivot2.columns]

df_merged = df0.set_index('PassengerId').join([df_pivot1, df_pivot2])

df_merged = df_merged.reset_index()

if 'Fare_1' in df_merged.columns and 'Fare_2' in df_merged.columns:
    df_merged = df_merged.rename(columns={'Fare_1': 'Fare_x', 'Fare_2': 'Fare_y'})
elif 'Fare_1' in df_merged.columns:
    df_merged = df_merged.rename(columns={'Fare_1': 'Fare_x'})
    df_merged['Fare_y'] = pd.NA
elif 'Fare_2' in df_merged.columns:
    df_merged = df_merged.rename(columns={'Fare_2': 'Fare_y'})
    df_merged['Fare_x'] = pd.NA
else:
    df_merged['Fare_x'] = pd.NA
    df_merged['Fare_y'] = pd.NA

cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df_final = df_merged[cols]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)