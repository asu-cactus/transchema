import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv"
source0_copy_path = "autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df0_copy = pd.read_csv(source0_copy_path, index_col=0)

# Join on PassengerId
df_merged = pd.merge(df0, df0_copy, on="PassengerId", suffixes=('_x', '_y'))

# Drop rows with any NaN values to match target row count and avoid missing data
df_merged = df_merged.dropna(how='any')

# Select columns as per target schema, renaming columns to remove suffixes except for Fare_x and Fare_y
df_result = pd.DataFrame()
df_result['PassengerId'] = df_merged['PassengerId']
df_result['Survived'] = df_merged['Survived_x']
df_result['Pclass'] = df_merged['Pclass_x']
df_result['Name'] = df_merged['Name_x']
df_result['Sex'] = df_merged['Sex_x']
df_result['Age'] = df_merged['Age_x']
df_result['SibSp'] = df_merged['SibSp_x']
df_result['Parch'] = df_merged['Parch_x']
df_result['Ticket'] = df_merged['Ticket_x']
df_result['Fare'] = df_merged['Fare_x']  # The first Fare column (original Fare)
df_result['Cabin'] = df_merged['Cabin_x']
df_result['Embarked'] = df_merged['Embarked_x']
df_result['Fare_x'] = df_merged['Fare_x']  # The Fare_x column (from first table)
df_result['Fare_y'] = df_merged['Fare_y']  # The Fare_y column (from second table)

# Write to CSV
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)