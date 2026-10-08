import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

# The source has columns: ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked']
# The target has additional columns Fare_x and Fare_y which are not in source.
# Since only one source table is given, and target has Fare_x and Fare_y, these likely come from pivoting or aggregation.

# The partial plan says PIVOT and GROUP_BY on PassengerId.
# We pivot Fare column to get Fare_x and Fare_y by some categorical column.
# The source does not have Fare_x or Fare_y, so we need to create them by pivoting Fare on some column.
# The target examples show Fare_x=10.5 and Fare_y=263.0 for some rows.
# Possibly Fare_x and Fare_y come from pivoting Fare by 'Pclass' or 'Survived' or 'Embarked'.
# Since the target has Fare_x and Fare_y, and source has Fare, we can pivot Fare by 'Survived' or 'Pclass'.
# Let's try pivoting Fare by 'Survived' to get Fare_x and Fare_y.

# Pivot Fare by Survived for each PassengerId
pivot_fare = df0.pivot(index='PassengerId', columns='Survived', values='Fare')
pivot_fare.columns = ['Fare_0', 'Fare_1'] if 0 in pivot_fare.columns and 1 in pivot_fare.columns else pivot_fare.columns

# Rename columns to Fare_x and Fare_y to match target
# From target examples, Fare_x and Fare_y are floats, so assign Fare_x = Fare_0, Fare_y = Fare_1
# If only one survived class exists, fill the other with NaN
fare_x = pivot_fare.get(0, pd.Series(dtype=float))
fare_y = pivot_fare.get(1, pd.Series(dtype=float))
pivot_fare = pd.DataFrame({'Fare_x': fare_x, 'Fare_y': fare_y})

# Now group by PassengerId and take first for other columns (since PassengerId is unique key)
grouped = df0.groupby('PassengerId').first()

# Merge pivot_fare with grouped on PassengerId
result = grouped.merge(pivot_fare, left_index=True, right_index=True, how='left')

# Reorder columns to match target schema
cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
result = result.reset_index()
result = result[cols]

# Ensure data types match target schema
result['PassengerId'] = result['PassengerId'].astype(int)
result['Survived'] = result['Survived'].astype(int)
result['Pclass'] = result['Pclass'].astype(int)
result['Name'] = result['Name'].astype(str)
result['Sex'] = result['Sex'].astype(str)
result['Age'] = result['Age'].astype(float)
result['SibSp'] = result['SibSp'].astype(int)
result['Parch'] = result['Parch'].astype(int)
result['Ticket'] = result['Ticket'].astype(str)
result['Fare'] = result['Fare'].astype(float)
result['Cabin'] = result['Cabin'].astype(str)
result['Embarked'] = result['Embarked'].astype(str)
result['Fare_x'] = result['Fare_x'].astype(float)
result['Fare_y'] = result['Fare_y'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)