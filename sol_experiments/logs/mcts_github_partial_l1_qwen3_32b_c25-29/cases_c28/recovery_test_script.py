import pandas as pd

df_school = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_28/test_0.csv")
df_student = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_28/test_1.csv")

merged_df = pd.merge(df_student, df_school, on="school_name", how="left")

merged_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_28/target_multisource_mcts_recovery_test_val.csv", index=False)