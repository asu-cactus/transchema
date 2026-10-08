import pandas as pd
import os

os.makedirs('autopipeline-benchmarks/github-pipelines/length4_98', exist_ok=True)

src_path = 'autopipeline-benchmarks/github-pipelines/length4_98/test_0.csv'
df = pd.read_csv(src_path, index_col=0)

# Apply GROUP BY operation
df = df.groupby('PassengerId', as_index=False).first()

# Add missing columns with NaN as they're not present in source data
df['Fare_x'] = float('NaN')
df['Fare_y'] = float('NaN')

# Save result
output_path = 'autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts_recovery_test_val.csv'
df.to_csv(output_path, index=False)