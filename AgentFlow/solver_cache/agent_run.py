import pandas as pd

# Step 1: Load the data from the source CSV file
source_df = pd.read_csv('/path/to/Source4_85_0.csv', index_col=0)

# Step 2: Project the required columns and rename 'crit_rank' to 'critic'
projected_df = source_df[['crit_cn', 'crit_rank']].rename(columns={'crit_rank': 'critic'})

# Step 3: Remove rows with NaN values from the specified columns
cleaned_df = projected_df.dropna(subset=['crit_cn', 'critic'])

# Step 4: Drop duplicate rows based on 'crit_cn' and 'critic'
unique_df = cleaned_df.drop_duplicates(subset=['crit_cn', 'critic'])

# Step 5: Save the resulting DataFrame to the specified CSV file
unique_df.to_csv('/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_agentic.csv', index=False)