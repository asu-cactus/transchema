import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

pivoted = df0.pivot_table(index='PassengerId', aggfunc='first').reset_index()

pivoted['Fare_x'] = df0.groupby('PassengerId')['Fare'].transform('mean')
pivoted['Fare_y'] = df0.groupby('PassengerId')['Fare'].transform('count').astype(int)

pivoted = pivoted.rename(columns={'Fare': 'Fare'})

cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
result = pivoted[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)