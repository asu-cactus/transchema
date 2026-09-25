import pandas as pd

source0_path = 'autopipeline-benchmarks/github-pipelines/length1_69/test_0.csv'
source1_path = 'autopipeline-benchmarks/github-pipelines/length1_69/test_1.csv'
target_path = 'autopipeline-benchmarks/github-pipelines/length1_69/target_multisource_mcts_recovery_test_val.csv'

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Step 1: Group by city and deduplicate
df0_grouped = df0.groupby('city', as_index=False).agg(
    driver_count=('driver_count', 'first'), 
    type=('type', 'first')
)

# Step 2: Join with source1
result = pd.merge(df0_grouped, df1, on='city', how='inner')

result.to_csv(target_path)