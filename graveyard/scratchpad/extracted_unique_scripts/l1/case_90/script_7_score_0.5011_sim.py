import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

df['doggo'] = df['doggo'].fillna('')
df['floofer'] = df['floofer'].fillna('')
df['pupper'] = df['pupper'].fillna('')
df['puppo'] = df['puppo'].fillna('')

def dog_type(row):
    if row['doggo'] == 'doggo':
        return 2
    elif row['floofer'] == 'floofer':
        return 3
    elif row['pupper'] == 'pupper':
        return 1
    elif row['puppo'] == 'puppo':
        return 4
    else:
        return 0

df['dog_type'] = df.apply(dog_type, axis=1)

result = df.groupby('dog_type').agg({'tweet_id':'count'}).reset_index()

result = result.rename(columns={'tweet_id':'dog_type_count'})

# The target schema only requires 'dog_type' column, so we keep only that column with counts as rows
# But target examples show dog_type as integer values with counts as values, so we output dog_type and counts as rows
# So we output dog_type and count as rows, but target schema only has dog_type column, so we output dog_type repeated count times

# To match target schema (only dog_type column), we expand rows by count
expanded_rows = []
for _, row in result.iterrows():
    expanded_rows.extend([row['dog_type']] * row['dog_type_count'])

final_df = pd.DataFrame({'dog_type': expanded_rows})

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)