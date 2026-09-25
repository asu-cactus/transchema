import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

pivot_df = df0.pivot(index='school_name', columns='type', values=['size', 'budget'])
pivot_df.columns = [f"{val}_{typ}" for val, typ in pivot_df.columns]
pivot_df = pivot_df.reset_index()

# From target schema and examples, 'a' is 'type' (string), 'b' is size (int), 'c' is budget (int)
# The pivot created columns like size_Charter, size_District, budget_Charter, budget_District
# But target examples show only one 'a' column (type), and one 'b' and 'c' column (size and budget)
# So we need to melt back or select the correct type per school_name.
# Actually, each school_name has only one type, so pivot is not needed here.
# The partial plan says PIVOT, but here pivot is not the best approach.
# Instead, we can just rename columns from df0 and join with df1.

# Reconsider plan: The first source has school_name, type, size, budget
# The target has school_name, a (type), b (size), c (budget)
# The second source has reading_score and math_score per student, grouped by school_name
# So we need to aggregate reading_score and math_score by school_name (mean)
# Then join with df0 on school_name
# So PIVOT is not needed, but since partial plan says PIVOT, we can interpret pivot as a no-op or skip it.

# Implementing the correct plan:

df0_renamed = df0.rename(columns={'type': 'a', 'size': 'b', 'budget': 'c'})
df0_renamed['b'] = df0_renamed['b'].astype(int)
df0_renamed['c'] = df0_renamed['c'].astype(int)

agg_scores = df1.groupby('school_name').agg({'reading_score': 'mean', 'math_score': 'mean'}).reset_index()
agg_scores = agg_scores.rename(columns={'reading_score': 'd', 'math_score': 'e'})
agg_scores['d'] = agg_scores['d'].astype(float)
agg_scores['e'] = agg_scores['e'].astype(float)

result = pd.merge(df0_renamed[['school_name', 'a', 'b', 'c']], agg_scores, on='school_name', how='inner')

result = result[['school_name', 'a', 'b', 'c', 'd', 'e']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)