import pandas as pd

source_path_0 = "autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv"

df0 = pd.read_csv(source_path_0, index_col=0)

df_unpivot = df0.melt(id_vars=['PassengerId'], value_vars=['Fare'], var_name='Fare_x', value_name='Fare_y')
df_unpivot.rename(columns={'Fare': 'Fare_x', 'Fare_y': 'Fare_y'}, inplace=True)

df_merged = pd.merge(df_unpivot, df0, on='PassengerId', suffixes=('_x', '_y'))

df_merged = df_merged[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare_x', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

df_merged.rename(columns={'Fare_x': 'Fare_x', 'Fare_y': 'Fare_y'}, inplace=True)

df_merged = df_merged[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare_x', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

df_merged = df_merged.loc[:,~df_merged.columns.duplicated()]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)