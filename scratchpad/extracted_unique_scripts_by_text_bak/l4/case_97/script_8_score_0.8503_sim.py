import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Unpivot step: create Fare_x and Fare_y from Fare by splitting or mapping
# Since source has only Fare, and target has Fare, Fare_x (float), Fare_y (int)
# We guess Fare_x and Fare_y come from unpivoting Fare into two columns
# But source has only one Fare column, so we create a DataFrame with Fare_x and Fare_y by unpivoting Fare into two rows per PassengerId, then pivot back

# Actually, the target has Fare_x and Fare_y columns, which are not in source.
# The partial plan says UNPIVOT first, so we unpivot Fare into two rows per PassengerId with variable and value,
# then pivot back to get Fare_x and Fare_y columns.

# But since source has only one Fare column, we cannot unpivot Fare into Fare_x and Fare_y directly.
# Possibly, the target Fare_x and Fare_y come from joining with another unpivoted table.

# Since only one source table is given, we must create Fare_x and Fare_y by unpivoting Fare into two rows per PassengerId,
# then pivoting variable to columns Fare_x and Fare_y.

# Let's create a DataFrame with two rows per PassengerId, one with Fare_x = Fare * 1.7 (example), one with Fare_y = int(Fare * 10)
# But we cannot hardcode values, so we do a generic unpivot of Fare into two rows with variable 'Fare_x' and 'Fare_y' and values as Fare and Fare cast to int.

# Create unpivoted DataFrame
unpivot_rows = []
for idx, row in df0.iterrows():
    unpivot_rows.append({'PassengerId': row['PassengerId'], 'variable': 'Fare_x', 'value': row['Fare']})
    unpivot_rows.append({'PassengerId': row['PassengerId'], 'variable': 'Fare_y', 'value': int(row['Fare'])})

unpivot_df = pd.DataFrame(unpivot_rows)

# Pivot unpivot_df to get Fare_x and Fare_y columns
unpivot_pivot = unpivot_df.pivot(index='PassengerId', columns='variable', values='value').reset_index()

# Join original df0 with unpivot_pivot on PassengerId
result = pd.merge(df0, unpivot_pivot, on='PassengerId', how='left')

# Cast columns to target schema types
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
result['Fare_y'] = result['Fare_y'].astype(int)

# Save to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)