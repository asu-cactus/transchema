import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

df0_sub = df0[['Publisher']].copy()
df1_sub = df1[['hero_names']].copy()
# Source1_96_1 does not have 'Publisher' column, so we cannot union directly.
# According to the plan, UNION is expected, but schemas differ.
# We must reconsider: since Source1_96_1 has no 'Publisher' column, UNION is impossible.
# Instead, we should only use Source1_96_0 for the target 'Publisher' column.

# So the plan must be corrected:
# Only Source1_96_0 has 'Publisher' column.
# Target schema is ['Publisher': integer], but source Publisher values are strings like 'DC Comics', 'Marvel Comics'.
# We need to convert Publisher strings to integer IDs.
# So:
# 1) Extract Publisher column from Source1_96_0
# 2) Map unique Publisher strings to integer IDs starting from 1
# 3) Group by Publisher string to get unique publishers (or just unique mapping)
# 4) Output the mapping as the target table.

# Since Source1_96_1 has no Publisher column, it cannot contribute to the target.

# Revised plan:
# GROUP_BY : [Publisher]
# MAP Publisher strings to integer IDs
# NO_MORE_OPERATION

# Implementing revised plan:

publishers = df0['Publisher'].dropna().unique()
publisher_map = {name: idx+1 for idx, name in enumerate(sorted(publishers))}
df_result = pd.DataFrame({'Publisher': df0['Publisher'].map(publisher_map)})
df_result = df_result.drop_duplicates().reset_index(drop=True)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)