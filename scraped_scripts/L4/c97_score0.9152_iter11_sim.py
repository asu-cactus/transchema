import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

df_pivot_0 = df0.pivot(index='PassengerId', columns='Embarked', values='Fare').reset_index()

df_pivot_1 = df0.pivot(index='PassengerId', columns='Sex', values='Fare').reset_index()

df_merged = pd.merge(df0, df_pivot_0[['PassengerId', 'C', 'Q', 'S']], on='PassengerId', how='left')
df_merged = pd.merge(df_merged, df_pivot_1[['PassengerId', 'female', 'male']], on='PassengerId', how='left')

df_merged = df_merged.rename(columns={'C': 'Fare_C', 'Q': 'Fare_Q', 'S': 'Fare_S', 'female': 'Fare_female', 'male': 'Fare_male'})

df_merged['Fare_x'] = df_merged['Fare_female'].combine_first(df_merged['Fare_male'])
df_merged['Fare_y'] = df_merged['Fare_C'].combine_first(df_merged['Fare_Q']).fillna(0).astype(int)

result = df_merged[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)