import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)
union_df = pd.concat([df0, df8, df9], ignore_index=True)

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
join1 = pd.merge(union_df, df2, on="ROW_WID", how="inner")

df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
join2 = pd.merge(join1, df3, on="ROW_WID", how="inner")

df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
join3 = pd.merge(join2, df4, on="ROW_WID", how="inner")

df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
join4 = pd.merge(join3, df5, on="ROW_WID", how="inner")

df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
join5 = pd.merge(join4, df6, on="ROW_WID", how="inner")

df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)
join6 = pd.merge(join5, df7, on="ROW_WID", how="inner")

result = join6.groupby("TECHSUPPORT_NUM", as_index=False).size().rename(columns={"size": "TECHSUPPORT_NUM"})
# The above line counts rows per TECHSUPPORT_NUM, but target schema is just TECHSUPPORT_NUM integer values (counts).
# Actually, target examples show TECHSUPPORT_NUM as integer values, not counts.
# So we just need to group by TECHSUPPORT_NUM and count rows, but target schema is just TECHSUPPORT_NUM column with counts as values.
# The example shows TECHSUPPORT_NUM values like 23,4,2, which are counts of something? Or just the values of TECHSUPPORT_NUM?
# The target schema is ['TECHSUPPORT_NUM': integer], and examples show values like 23,4,2.
# The partial plan says UNPIVOT then GROUP_BY on TECHSUPPORT_NUM.
# But we have no unpivot needed here because TECHSUPPORT_NUM is already a column.
# The best interpretation is to count how many rows per TECHSUPPORT_NUM.
# So the output should be a dataframe with columns TECHSUPPORT_NUM and count.
# But the target schema only has TECHSUPPORT_NUM column, so likely the count is the value of TECHSUPPORT_NUM itself.
# The source4 has TECHSUPPORT_NUM column, so we just need to get distinct TECHSUPPORT_NUM values from source4.
# But the plan says GROUP_BY TECHSUPPORT_NUM, so we do groupby and count rows per TECHSUPPORT_NUM.
# Let's produce a dataframe with TECHSUPPORT_NUM and counts, rename counts column to TECHSUPPORT_NUM to match target schema.
# But that would overwrite the column, so better to just output the counts as TECHSUPPORT_NUM column.
# So final output is counts per TECHSUPPORT_NUM, with column named TECHSUPPORT_NUM.

counts = join6.groupby("TECHSUPPORT_NUM").size().reset_index(name="count")
counts = counts.rename(columns={"count": "TECHSUPPORT_NUM"})

counts.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)