import pandas as pd
import glob

# Read all source files with the same schema
sources = [
    'autopipeline-benchmarks/github-pipelines/length9_78/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_4.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_5.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_6.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_7.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_8.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_9.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_10.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_11.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_12.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_13.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_14.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_15.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_16.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_17.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_18.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_19.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_20.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_21.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_22.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_23.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_24.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_25.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_26.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_27.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_28.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_29.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_30.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_31.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_32.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_33.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_34.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_35.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_36.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_37.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_38.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_39.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_40.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_41.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_42.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_43.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_44.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_45.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_46.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_47.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_48.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_49.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_50.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_51.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_52.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_53.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_54.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_55.csv',
    'autopipeline-benchmarks/github-pipelines/length9_78/test_56.csv'
]

# Read each source file and combine using pd.concat
dfs = []
for src in sources:
    df = pd.read_csv(src, index_col=0)
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)

# Drop duplicates if any (unlikely but just in case)
combined_df = combined_df.drop_duplicates()

# Save the final output
combined_df.to_csv('autopipeline-benchmarks/github-pipelines/length9_78/target_multisource_mcts_recovery_test_val.csv', index=False)