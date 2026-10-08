import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

def extract_dog_type(row):
    if pd.notna(row['doggo']):
        return 1
    if pd.notna(row['floofer']):
        return 2
    if pd.notna(row['pupper']):
        return 3
    if pd.notna(row['puppo']):
        return 4
    return 0

df0['dog_type'] = df0.apply(extract_dog_type, axis=1)
result = df0.groupby('dog_type', as_index=False).size()
result = result.rename(columns={'size': 'dog_type_count'})  # temporary rename to avoid confusion

# The target schema is ['dog_type': integer], and target examples show dog_type values 1,2,3,4 with counts.
# The target table only has one column dog_type, so we output distinct dog_type values with their counts.
# But target schema only has dog_type column, no count column.
# The target examples show dog_type values with counts as values, so likely the target table is dog_type with counts as values.
# But the target schema is only dog_type integer column, so the counts are the values of dog_type column.
# This means the target table is a frequency table with dog_type as the value column.
# So we rename the count column to dog_type and drop the original dog_type column.

result = result.rename(columns={'dog_type': 'dog_type', 'dog_type_count': 'dog_type'})
result = result[['dog_type']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)