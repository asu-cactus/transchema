import pandas as pd

# Read all source files with index_col=0
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_9.csv", index_col=0)

# Drop extra columns in src2 to match schema of other similar sources
src2 = src2.drop(columns=[col for col in ['5040', '100.00%'] if col in src2.columns])

# List of sources with same schema to union
union_sources = [src0, src2, src3, src4, src5, src6, src7, src8, src9]

# Union all these sources (concatenate)
unioned = pd.concat(union_sources, ignore_index=True, sort=False)

# Join unioned with src1 on bid_id = sampled_bid_id only (not on message_timestamp)
merged = pd.merge(
    unioned,
    src1,
    left_on='bid_id',
    right_on='sampled_bid_id',
    how='inner',
    suffixes=('_x', '_y')
)

# Drop sampled_bid_id as it's redundant after join
if 'sampled_bid_id' in merged.columns:
    merged = merged.drop(columns=['sampled_bid_id'])

# Group by bid_id and message_timestamp (leftmost unique keys) to remove duplicates
# No aggregation needed, just drop duplicates by these keys keeping first occurrence
merged = merged.sort_values(by=['bid_id', 'message_timestamp'])
merged = merged.drop_duplicates(subset=['bid_id', 'message_timestamp'], keep='first')

# Rename columns to match target schema exactly
# Mapping columns from left (unioned) source (suffix _x) and right (src1) source (suffix _y)
rename_map = {}

# Columns from unioned sources (left) - suffix _x
for col in unioned.columns:
    if col in ['bid_id', 'message_timestamp']:
        rename_map[col] = col
    else:
        rename_map[col] = f"{col}_x"

# Columns from src1 (right) - suffix _y
for col in src1.columns:
    if col in ['sampled_bid_id', 'message_timestamp']:
        continue  # already handled or dropped
    else:
        # For 'message_sender' in src1, rename to 'message_sender_y'
        if col == 'message_sender':
            rename_map[col] = 'message_sender_y'
        else:
            rename_map[col] = col

# After merge, columns from src1 have suffix _y added by pandas, so adjust accordingly
final_rename = {}
for col in merged.columns:
    if col in rename_map:
        final_rename[col] = rename_map[col]
    else:
        # For columns with suffixes added by pandas
        if col.endswith('_x') or col.endswith('_y'):
            base_col = col[:-2]
            if base_col in rename_map:
                final_rename[col] = rename_map[base_col]
            else:
                final_rename[col] = col
        else:
            final_rename[col] = col

merged = merged.rename(columns=final_rename)

# The target schema has many columns with suffixes and repeated label columns.
# The above renaming aligns columns with suffixes _x and _y as in target schema.

# Reorder columns to match target schema order
target_columns = ['bid_id', 'message_timestamp', 'message_sender_x', 'message', 'category_x', 'agent_group', 'bid_id_header_x',
                  'message_sender_y', 'pii_cleaned_message_x', 'Label 1_x_x', 'Label 2_x_x', 'Label 3_x_x', 'Label 4_x_x', 'Label 5_x_x', 'Note_x',
                  'category_y', 'Label 1_y_x', 'Label 2_y_x', 'Label 3_y_x', 'Label 4_y_x', 'Label 5_y_x',
                  'Label 1_x_x_21', 'Label 2_x_x_22', 'Label 3_x_x_23', 'Label 4_x_x_24', 'Label 5_x_x_25', 'bid_id_header_y',
                  'message_sender_x_27', 'pii_cleaned_message_y', 'Label 1_x_y', 'Label 2_x_y', 'Label 3_x_y', 'Label 4_x_y', 'Label 5_x_y', 'Note_y',
                  'category_x_35', 'Label 1_y_y', 'Label 2_y_y', 'Label 3_y_y', 'Label 4_y_y', 'Label 5_y_y',
                  'Label 1_y_x_41', 'Label 2_y_x_42', 'Label 3_y_x_43', 'Label 4_y_x_44', 'Label 5_y_x_45', 'bid_id_header_x_46',
                  'message_sender_y_47', 'pii_cleaned_message_x_48', 'Label 1_x_y_49', 'Label 2_x_y_50', 'Label 3_x_y_51', 'Label 4_x_y_52', 'Label 5_x_y_53', 'Note_x_54',
                  'category_y_55', 'Label 1_y_y_56', 'Label 2_y_y_57', 'Label 3_y_y_58', 'Label 4_y_y_59', 'Label 5_y_y_60',
                  'Label 1_x_x_61', 'Label 2_x_x_62', 'Label 3_x_x_63', 'Label 4_x_x_64', 'Label 5_x_x_65', 'bid_id_header_y_66',
                  'message_sender_x_67', 'pii_cleaned_message_y_68', 'Label 1_x_x_69', 'Label 2_x_x_70', 'Label 3_x_x_71', 'Label 4_x_x_72', 'Label 5_x_x_73', 'Note_y_74',
                  'category_x_75', 'Label 1_y_x_76', 'Label 2_y_x_77', 'Label 3_y_x_78', 'Label 4_y_x_79', 'Label 5_y_x_80',
                  'Label 1_y_x_81', 'Label 2_y_x_82', 'Label 3_y_x_83', 'Label 4_y_x_84', 'Label 5_y_x_85', 'bid_id_header_x_86',
                  'message_sender_y_87', 'pii_cleaned_message_x_88', 'Label 1_x_y_89', 'Label 2_x_y_90', 'Label 3_x_y_91', 'Label 4_x_y_92', 'Label 5_x_y_93', 'Note_x_94',
                  'category_y_95', 'Label 1_y_y_96', 'Label 2_y_y_97', 'Label 3_y_y_98', 'Label 4_y_y_99', 'Label 5_y_y_100',
                  'Label 1_x', 'Label 2_x', 'Label 3_x', 'Label 4_x', 'Label 5_x', 'bid_id_header_y_106', 'message_sender', 'pii_cleaned_message_y_108',
                  'Label 1_x_109', 'Label 2_x_110', 'Label 3_x_111', 'Label 4_x_112', 'Label 5_x_113', 'Note_y_114', 'category',
                  'Label 1_y', 'Label 2_y', 'Label 3_y', 'Label 4_y', 'Label 5_y', 'Label 1_y_121', 'Label 2_y_122', 'Label 3_y_123', 'Label 4_y_124', 'Label 5_y_125']

# Keep only columns present in merged
final_columns = [col for col in target_columns if col in merged.columns]

merged = merged[final_columns]

# Write output
merged.to_csv("autopipeline-benchmarks/github-pipelines/length9_70/target_multisource_mcts.csv", index=False)