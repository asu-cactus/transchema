import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv"
df0 = pd.read_csv(src0_path, index_col=0)

# Join the table with itself on PassengerId
df_joined = pd.merge(df0, df0, on="PassengerId", suffixes=('_x', '_y'))

# Group by PassengerId to ensure uniqueness, aggregate other columns by first()
agg_dict = {
    'Survived': 'first',
    'Pclass': 'first',
    'Name': 'first',
    'Sex': 'first',
    'Age': 'first',
    'SibSp': 'first',
    'Parch': 'first',
    'Ticket': 'first',
    'Fare': 'first',
    'Cabin': 'first',
    'Embarked': 'first',
    'Fare_x': 'first',
    'Fare_y': 'first'
}

result = df_joined.groupby('PassengerId', as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
result = result[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)