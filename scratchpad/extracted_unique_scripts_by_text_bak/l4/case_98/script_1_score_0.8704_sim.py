import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

# The partial plan suggests PIVOT and GROUP_BY on Name.
# Since we have only one source table, and the target schema has Fare_x and Fare_y columns,
# which do not exist in source, we need to create these columns.
# The target examples show Fare_x and Fare_y have values different from Fare.
# Since only one source is given, we can assume Fare_x and Fare_y are derived by pivoting Fare by some category.
# But no other source or column is given to pivot on.
# The partial plan says PIVOT and GROUP_BY on Name.
# Let's try to pivot Fare by Sex (male/female) to get Fare_x and Fare_y.
# But the target examples show Fare_x and Fare_y are floats and differ from Fare.
# Possibly Fare_x and Fare_y are Fare values pivoted by Sex or Pclass or Embarked.
# Let's try pivoting Fare by Sex to get Fare_x and Fare_y.

# Pivot Fare by Sex for each Name
pivot_fare = df0.pivot_table(index='Name', columns='Sex', values='Fare', aggfunc='first')

# Rename columns to Fare_x and Fare_y (assuming male->Fare_x, female->Fare_y)
# But target examples show Fare_x and Fare_y both present for each row.
# So we join back to original df0 on Name to get all columns plus Fare_x and Fare_y.

pivot_fare = pivot_fare.rename(columns={'male': 'Fare_x', 'female': 'Fare_y'})

df = df0.merge(pivot_fare, on='Name', how='left')

# Ensure columns are in target schema order and types
target_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

df = df[target_cols]

# Cast types according to target schema
df['PassengerId'] = df['PassengerId'].astype(int)
df['Survived'] = df['Survived'].astype(int)
df['Pclass'] = df['Pclass'].astype(int)
df['Name'] = df['Name'].astype(str)
df['Sex'] = df['Sex'].astype(str)
df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
df['SibSp'] = df['SibSp'].astype(int)
df['Parch'] = df['Parch'].astype(int)
df['Ticket'] = df['Ticket'].astype(str)
df['Fare'] = pd.to_numeric(df['Fare'], errors='coerce')
df['Cabin'] = df['Cabin'].astype(str).replace('nan', pd.NA)
df['Embarked'] = df['Embarked'].astype(str).replace('nan', pd.NA)
df['Fare_x'] = pd.to_numeric(df['Fare_x'], errors='coerce')
df['Fare_y'] = pd.to_numeric(df['Fare_y'], errors='coerce')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)