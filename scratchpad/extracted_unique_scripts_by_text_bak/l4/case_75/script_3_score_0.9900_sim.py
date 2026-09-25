import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_1.csv", index_col=0)

# Source4_75_0 has columns: ['School ID', 'school_name', 'type', 'size', 'budget']
# Source4_75_1 has columns: ['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score']
# They have different schemas, so UNION is not possible directly.

# The partial plan suggests UNION of Source4_75_0 and Source4_75_1, but schemas differ.
# According to hints, JOIN is preferred if schemas differ and share common columns.
# Common column is 'school_name' and 'type' only in Source4_75_0.
# Source4_75_1 does not have 'type' column.
# So we need to join Source4_75_1 with Source4_75_0 on 'school_name' to get 'type' for each student.

# After join, we can group by 'type' and aggregate to get columns 'a' and 'b' matching target schema.
# Target columns 'a' and 'b' are floats.
# From target examples, 'a' and 'b' seem to be some aggregated numeric values per 'type'.
# Possible candidates:
# - 'a' could be average reading_score per type
# - 'b' could be average math_score per type
# Or
# - 'a' could be average size per type
# - 'b' could be average budget per type
# But target examples show values around 76-83 for 'a' and 'b', which matches scores better than size or budget.

# So plan:
# 1) Join df1 with df0 on 'school_name' to get 'type' for each student.
# 2) Group by 'type' and aggregate average reading_score as 'a' and average math_score as 'b'.
# 3) Save result.

# Implementing this plan:

df_joined = pd.merge(df1, df0[['school_name', 'type']], on='school_name', how='inner')

result = df_joined.groupby('type').agg(
    a=pd.NamedAgg(column='reading_score', aggfunc='mean'),
    b=pd.NamedAgg(column='math_score', aggfunc='mean')
).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)