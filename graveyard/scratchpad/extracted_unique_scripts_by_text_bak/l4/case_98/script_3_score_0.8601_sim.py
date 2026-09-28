import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

df_fares = df0[['PassengerId', 'Fare']].copy()
df_fares['key'] = 'Fare'
df_fares['Fare_value'] = df_fares['Fare']
df_fares = df_fares.pivot(index='PassengerId', columns='key', values='Fare_value').reset_index()

df_fares_x = df0[['PassengerId', 'Fare']].rename(columns={'Fare': 'Fare_x'})
df_fares_y = df0[['PassengerId', 'Fare']].rename(columns={'Fare': 'Fare_y'})

df_unpivot = pd.DataFrame({
    'PassengerId': df0['PassengerId'],
    'Fare_x': df_fares_x['Fare_x'],
    'Fare_y': df_fares_y['Fare_y']
})

df_result = df0.merge(df_unpivot, on='PassengerId')

df_result = df_result[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)