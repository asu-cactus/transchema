import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

result = df0.groupby("Publisher", dropna=False).agg({"name": "count"}).reset_index()
result = result.rename(columns={"name": "Publisher"})
result.columns = ["Publisher", "count"]  # temporarily rename count column

# The target schema is ['Publisher': integer], and target examples show Publisher as integer counts.
# So we want to output a dataframe with columns: Publisher (int)
# The target examples show Publisher column with integer values like 1,7,1, which matches count of names per Publisher.
# So we rename the count column to Publisher to match target schema.

# But the target schema is just one column named Publisher with integer values.
# So we should output the count as Publisher column, dropping the original Publisher string column.

# So final output is the count of names per Publisher, with column named Publisher.

result = result.rename(columns={"count": "Publisher"})
result = result[["Publisher"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)