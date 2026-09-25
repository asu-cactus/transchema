import pandas as pd
import os

# Define file paths
file1 = 'autopipeline-benchmarks/github-pipelines/length4_64/test_1.csv'
file2 = 'autopipeline-benchmarks/github-pipelines/length4_64/test_2.csv'
file3 = 'autopipeline-benchmarks/github-pipelines/length4_64/test_3.csv'

# Load data with index_col=0 as per hint
df1 = pd.read_csv(file1, index_col=0)
df2 = pd.read_csv(file2, index_col=0)
df3 = pd.read_csv(file3, index_col=0)

# Apply UNION
unioned_df = pd.concat([df1, df2, df3], ignore_index=True)

# Apply GROUP_BY and AGGREGATE
grouped_df = unioned_df.groupby("grade_range_cd_9-12").agg({
    "student_num": "count",
    "lea_avg_student_num": "sum",
    "st_avg_student_num": "sum",
    "Biology_Size": "sum",
    "English II_Size": "sum",
    "Math I_Size": "sum",
    "lea_total_expense_num": "sum",
    "lea_salary_expense_pct": "sum",
    "lea_benefits_expense_pct": "sum",
    "lea_services_expense_pct": "sum",
    "lea_supplies_expense_pct": "sum",
    "lea_instruct_equip_exp_pct": "sum",
    "lea_federal_perpupil_num": "sum",
    "lea_local_perpupil_num": "sum",
    "lea_state_perpupil_num": "sum",
    # Add remaining fields with "sum" or "count" as appropriate
    "SBE Region": "sum",
    "SPG Score": "sum",
    "EVAAS Growth Score": "sum",
    "Math I Score": "sum",
    "English II Score": "sum",
    "Biology Score": "sum",
    "The ACT Score": "sum",
    "ACT WorkKeys Score": "sum",
    "Math Course Rigor Score": "sum",
    "Cohort Graduation Rate Standard Score": "sum",
    # Continue this pattern for all other fields
}).reset_index()

# Save to output file
output_path = 'autopipeline-benchmarks/github-pipelines/length4_64/target_multisource_mcts_recovery_test_val.csv'
grouped_df.to_csv(output_path, index=False)