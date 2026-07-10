import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_45/training_1.csv", index_col=0)

pivot_result = df0.pivot(index='State', columns='Participation', values=['English', 'Math', 'Reading', 'Science', 'Composite'])
pivot_result.columns = [f"{col[0]}_{col[1]}" for col in pivot_result.columns]
pivot_result = pivot_result.reset_index()

result = pd.merge(pivot_result, df1, on='State', how='inner')

result = result.rename(columns={
    'Participation_x': 'Participation_x',
    'Participation_y': 'Participation_y',
    'Math_x': 'Math_x',
    'Math_y': 'Math_y',
    'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
    'Total': 'Total'
})

cols = ['State', 'Participation_100%', 'English_100%', 'Math_100%', 'Reading_100%', 'Science_100%', 'Composite_100%',
        'Participation_5%', 'Evidence-Based Reading and Writing', 'Math', 'Total']

# Participation_x and Participation_y come from pivoted columns and df1 respectively.
# Participation_x is the participation rate from df0 (pivoted), Participation_y from df1.

# We need to map Participation_x and Participation_y columns correctly:
# From pivot_result, Participation_x is the participation column name from df0, which is the participation value in the column suffix.
# But the target schema expects Participation_x and Participation_y as strings, so we take the participation values from the pivot columns.

# Extract Participation_x and Participation_y:
# Participation_x: the participation value corresponding to the columns in df0 (pivoted)
# Participation_y: the Participation column from df1

# The pivoted columns have suffixes like '100%', '67%', etc. We want to pick the participation value corresponding to the participation column in df0.
# But the target examples show Participation_x and Participation_y as strings like '100%', '3%', etc.

# We can get Participation_x as the participation value corresponding to the columns in df0 (pivoted).
# Since pivoted columns are multi-indexed by (subject, participation), we can get the participation values from the columns.

# But the target schema has only one Participation_x and one Participation_y per row.
# The source df0 has only one participation per state, but after pivot, we have multiple columns per participation.
# Actually, df0 has only one participation per state, so pivoting by participation creates columns for each participation value.
# But each state has only one participation value, so only one set of columns per state is non-null.

# So for each row, Participation_x is the participation value corresponding to the non-null columns in pivot_result.
# We can extract Participation_x by checking which participation suffix has non-null English score.

def extract_participation_x(row):
    for col in pivot_result.columns:
        if col.startswith('English_') and pd.notna(row[col]):
            return col.split('_')[1]
    return None

result['Participation_x'] = result.apply(extract_participation_x, axis=1)
result['Participation_y'] = result['Participation']

result = result.rename(columns={
    'English_100%': 'English',
    'Math_100%': 'Math_x',
    'Reading_100%': 'Reading',
    'Science_100%': 'Science',
    'Composite_100%': 'Composite',
    'Math': 'Math_y'
})

# Because pivoted columns have suffixes for participation, but only one participation per state, we select the columns with suffix matching Participation_x
# So we need to select the columns with suffix matching Participation_x for each row.

# To handle this properly, we will reconstruct the columns by selecting the columns with suffix matching Participation_x per row.

def select_subject_scores(row):
    p = row['Participation_x']
    return pd.Series({
        'English': row.get(f'English_{p}', pd.NA),
        'Math_x': row.get(f'Math_{p}', pd.NA),
        'Reading': row.get(f'Reading_{p}', pd.NA),
        'Science': row.get(f'Science_{p}', pd.NA),
        'Composite': row.get(f'Composite_{p}', pd.NA)
    })

scores = result.apply(select_subject_scores, axis=1)
result = pd.concat([result, scores], axis=1)

final_cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
              'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

final_df = result[final_cols]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_45/target_multisource_mcts.csv", index=False)