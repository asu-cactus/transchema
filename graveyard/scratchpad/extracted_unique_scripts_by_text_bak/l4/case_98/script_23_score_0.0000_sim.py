import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked'],
                      value_vars=['Fare'],
                      var_name='variable', value_name='value')

df_grouped = df_unpivot.groupby('Name', as_index=False).agg({
    'PassengerId': 'first',
    'Survived': 'first',
    'Pclass': 'first',
    'Sex': 'first',
    'Age': 'first',
    'SibSp': 'first',
    'Parch': 'first',
    'Ticket': 'first',
    'Fare': 'first',
    'Cabin': 'first',
    'Embarked': 'first',
    'value': 'sum'
})

df_grouped = df_grouped.rename(columns={'Fare': 'Fare_x', 'value': 'Fare_y'})

df_grouped = df_grouped[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare_x', 'Cabin', 'Embarked', 'Fare_y']]

df_grouped['PassengerId'] = df_grouped['PassengerId'].astype(int)
df_grouped['Survived'] = df_grouped['Survived'].astype(int)
df_grouped['Pclass'] = df_grouped['Pclass'].astype(int)
df_grouped['SibSp'] = df_grouped['SibSp'].astype(int)
df_grouped['Parch'] = df_grouped['Parch'].astype(int)
df_grouped['Age'] = df_grouped['Age'].astype(float)
df_grouped['Fare_x'] = df_grouped['Fare_x'].astype(float)
df_grouped['Fare_y'] = df_grouped['Fare_y'].astype(float)
df_grouped['Name'] = df_grouped['Name'].astype(str)
df_grouped['Sex'] = df_grouped['Sex'].astype(str)
df_grouped['Ticket'] = df_grouped['Ticket'].astype(str)
df_grouped['Cabin'] = df_grouped['Cabin'].astype(str)
df_grouped['Embarked'] = df_grouped['Embarked'].astype(str)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)