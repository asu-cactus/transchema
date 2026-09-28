import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

pivot_df = df0.pivot_table(index=['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Cabin', 'Embarked'],
                          values='Fare', aggfunc='sum').reset_index()

pivot_df['Fare_x'] = pivot_df['Fare']
pivot_df['Fare_y'] = pivot_df['Fare'].astype(int)
pivot_df = pivot_df.drop(columns=['Fare'])

pivot_df = pivot_df.groupby('Name', as_index=False).first()

pivot_df = pivot_df.astype({
    'PassengerId': 'int64',
    'Survived': 'int64',
    'Pclass': 'int64',
    'Name': 'string',
    'Sex': 'string',
    'Age': 'float64',
    'SibSp': 'int64',
    'Parch': 'int64',
    'Ticket': 'string',
    'Cabin': 'string',
    'Embarked': 'string',
    'Fare_x': 'float64',
    'Fare_y': 'int64'
})

pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)