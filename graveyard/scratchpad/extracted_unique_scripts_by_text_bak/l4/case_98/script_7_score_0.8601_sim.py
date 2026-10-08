import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

df_fare_x = df0[['PassengerId', 'Fare']].rename(columns={'Fare': 'Fare_x'})
df_fare_y = df0[['PassengerId', 'Fare']].rename(columns={'Fare': 'Fare_y'})

df = df0.merge(df_fare_x, on='PassengerId').merge(df_fare_y, on='PassengerId')

df = df.astype({
    'PassengerId': 'int64',
    'Survived': 'int64',
    'Pclass': 'int64',
    'Name': 'string',
    'Sex': 'string',
    'Age': 'float64',
    'SibSp': 'int64',
    'Parch': 'int64',
    'Ticket': 'string',
    'Fare': 'float64',
    'Cabin': 'string',
    'Embarked': 'string',
    'Fare_x': 'float64',
    'Fare_y': 'float64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)