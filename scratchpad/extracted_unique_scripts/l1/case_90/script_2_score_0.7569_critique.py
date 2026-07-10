import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

def extract_dog_type(row):
    for col, code in [('doggo', 0), ('floofer', 1), ('pupper', 2), ('puppo', 3)]:
        if pd.notna(row[col]) and row[col] != '':
            return code
    return 4

df['dog_type'] = df.apply(extract_dog_type, axis=1)

result = df.groupby('dog_type').size().reset_index(name='count')

# The target schema only has 'dog_type' column, so output dog_type values repeated count times
# But since target examples show counts as values, we output dog_type as integer values (the counts)
# The target examples show values like [4471], [107], [96], which are counts per dog_type.
# So we output the counts as dog_type values, ignoring the dog_type codes.

# So the final output is the counts per dog_type as rows with column dog_type.

result = result[['count']].rename(columns={'count': 'dog_type'})

result['dog_type'] = result['dog_type'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)