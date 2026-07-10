import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv", index_col=0)

# Ensure 'Source Zipcode' is integer type (strip if string)
df0['Source Zipcode'] = df0['Source Zipcode'].astype(str).str.strip()
df0['Source Zipcode'] = df0['Source Zipcode'].astype(int)

# Ensure 'Counts' is integer
df0['Counts'] = df0['Counts'].astype(int)

# Group by 'Source Zipcode' and sum 'Counts'
df_grouped = df0.groupby('Source Zipcode', as_index=False)['Counts'].sum()

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)