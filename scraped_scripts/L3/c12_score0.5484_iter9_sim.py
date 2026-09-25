import pandas as pd

src_path = "autopipeline-benchmarks/github-pipelines/length3_12/training_0.csv"
df0 = pd.read_csv(src_path, index_col=0)

# According to the plan, first join Source3_12_0 with itself on 'Item ID'
df_joined = pd.merge(df0, df0, on='Item ID', suffixes=('_left', '_right'))

# Then union Source3_12_0 with itself (concatenate)
df_union = pd.concat([df0, df0], ignore_index=True)

# The target schema is ['SN': string, 'Price': float, 'count': integer]
# From source, 'SN' and 'Price' exist, but 'count' does not.
# We can create 'count' as 1 for each row.

# Use the unioned dataframe to produce the target table
target_df = df_union[['SN', 'Price']].copy()
target_df['count'] = 1
target_df['SN'] = target_df['SN'].astype(str)
target_df['Price'] = target_df['Price'].astype(float)
target_df['count'] = target_df['count'].astype(int)

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_12/target_multisource_mcts.csv", index=False)