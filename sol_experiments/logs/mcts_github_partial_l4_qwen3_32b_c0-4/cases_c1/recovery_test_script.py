import pandas as pd

# Load all source tables
source4_1_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_1/test_0.csv", index_col=0)
source4_1_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_1/test_1.csv", index_col=0)
source4_1_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_1/test_2.csv", index_col=0)
source4_1_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_1/test_3.csv", index_col=0)

# Join Source4_1_1 and Source4_1_0
join1 = pd.merge(left=source4_1_1, right=source4_1_0, how="inner", left_on="COD_OFICIPAL", right_on="COD_OFICI")

# Join with Source4_1_2 on COD_PERSONA
join2 = pd.merge(left=join1, right=source4_1_2, how="inner", left_on="COD_PERSONA", right_on="COD_PERSONA")

# Join with Source4_1_3 on COD_IDCONTRA
final_df = pd.merge(left=join2, right=source4_1_3, how="inner", left_on="COD_IDCONTRA", right_on="COD_IDCONTRA")

# Save the result to the target file
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_1/target_multisource_mcts_recovery_test_val.csv")