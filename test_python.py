import pandas as pd

# Load the intermediate result after the group_by and avg aggregation operation
intermediate_path = "autopipeline-benchmarks/github-pipelines/intermediate_space/length1_3/intermediate_step1.csv"
df = pd.read_csv(intermediate_path, index_col=0)

# Ensure the schema and types match the target schema
df = df.rename(columns={"Median": "Median", "Major_category": "Major_category"})
df["Major_category"] = df["Major_category"].astype(str)
df["Median"] = df["Median"].astype(float)

# Reorder columns to match target schema exactly
df = df[["Major_category", "Median"]]

# Write the final target table to the specified path
output_path = "autopipeline-benchmarks/github-pipelines/length1_3/target_multisource.csv"
df.to_csv(output_path)