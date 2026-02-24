import pandas as pd

# Step 1: Load the data from the source CSV file
source_df = pd.read_csv('/path/to/test_1_84_0.csv', index_col=0)

# Step 2: Transform the 'V_CALL' column
source_df['V_CALL'] = source_df['V_CALL'].astype(str).fillna('UNKNOWN')
source_df['V_GENE'] = source_df['V_CALL'].apply(lambda x: x.split('*')[0] if '*' in x else x)

# Step 3: Project only the 'V_GENE' column
result_df = source_df[['V_GENE']]

# Step 4: Remove rows with NaN values in 'V_GENE'
result_df = result_df.dropna()

# Step 5: Save the output to the specified CSV file
result_df.to_csv('/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_agentic.csv', index=False)