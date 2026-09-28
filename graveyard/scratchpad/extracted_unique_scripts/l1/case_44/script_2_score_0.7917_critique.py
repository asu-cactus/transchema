import pandas as pd

# Read the single source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

# Convert 'Value' to numeric, coercing errors to NaN
df0['Value'] = pd.to_numeric(df0['Value'], errors='coerce')

# Group by 'Country / territory of asylum/residence' and sum 'Value'
grouped = df0.groupby('Country / territory of asylum/residence', as_index=False)['Value'].sum()

# Rename 'Value' to 'Year' to match target schema
result = grouped.rename(columns={'Value': 'Year'})

# Ensure 'Year' column is integer type, filling NaNs with 0 before conversion
result['Year'] = result['Year'].fillna(0).astype(int)

# Write the result to the target CSV file
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)