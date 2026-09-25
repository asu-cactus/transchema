import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="PassengerId", suffixes=('_x', '_y'))

df_grouped = df_joined.groupby('Name', as_index=False).agg({
    'PassengerId': 'first',
    'Survived': 'first',
    'Pclass': 'first',
    'Sex': 'first',
    'Age': 'first',
    'SibSp': 'first',
    'Parch': 'first',
    'Ticket': 'first',
    'Fare_x': 'first',
    'Cabin': 'first',
    'Embarked': 'first',
    'Fare_y': 'first'
})

df_grouped = df_grouped[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare_x', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

# The target schema expects Fare (original) as 'Fare' column, but after join we have Fare_x and Fare_y.
# The original Fare column is split into Fare_x and Fare_y after join.
# The target schema has Fare (float) and Fare_x, Fare_y (float).
# We keep Fare_x and Fare_y from join, but also need Fare (original) from source.
# Since Fare_x and Fare_y come from the join, and Fare (original) is missing, we add Fare from df0.

df_grouped['Fare'] = df_grouped['Fare_x']

df_grouped = df_grouped[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)