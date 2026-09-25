import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_70/training_1.csv", index_col=0)

merged = pd.merge(
    src0,
    src1,
    left_on=["bid_id", "message_timestamp"],
    right_on=["sampled_bid_id", "message_timestamp"],
    how="inner",
    suffixes=('_x', '_y')
)

# Rename columns to match target schema exactly
# The target schema has many columns with suffixes and repeated label columns.
# We keep all columns from both sources with suffixes as pandas merged them.
# Also, rename columns to match target schema names exactly.

# Rename columns from src0 (left) with suffix _x if not already suffixed
rename_map = {
    'bid_id': 'bid_id',
    'message_timestamp': 'message_timestamp',
    'message_sender_x': 'message_sender_x',
    'message_sender': 'message_sender_x',
    'pii_cleaned_message': 'pii_cleaned_message_x',
    'Label 1': 'Label 1_x_x',
    'Label 2': 'Label 2_x_x',
    'Label 3': 'Label 3_x_x',
    'Label 4': 'Label 4_x_x',
    'Label 5': 'Label 5_x_x',
    'Note': 'Note_x',
    'category': 'category_x',
    'bid_id_header': 'bid_id_header_x'
}

# Rename columns from src1 (right) with suffix _y if not already suffixed
rename_map.update({
    'sampled_bid_id': 'sampled_bid_id',  # not needed in target, will drop later
    'message_sender_y': 'message_sender_y',
    'message_sender': 'message_sender_y',
    'message': 'message',
    'category_y': 'category_y',
    'agent_group': 'agent_group',
})

# Because pandas merge added suffixes _x and _y automatically, columns from src0 have _x suffix,
# columns from src1 have _y suffix, except for join keys.

# We will rename columns to target schema names by adjusting suffixes and names accordingly.

# First, rename columns to target names where possible
# For columns from src0, rename from original names to target names with _x suffix
# For columns from src1, rename from original names to target names with _y suffix

# But since pandas already added suffixes, we need to rename accordingly.

# Build a rename dictionary for columns in merged dataframe
rename_dict = {}

# For src0 columns (left), they have suffix _x added by pandas except join keys
for col in src0.columns:
    if col in ['bid_id', 'message_timestamp']:
        # These columns are join keys, appear without suffix
        rename_dict[col] = col
    else:
        # These columns have suffix _x in merged
        merged_col = col + '_x'
        if col == 'message_sender':
            rename_dict[merged_col] = 'message_sender_x'
        elif col == 'pii_cleaned_message':
            rename_dict[merged_col] = 'pii_cleaned_message_x'
        elif col == 'Label 1':
            rename_dict[merged_col] = 'Label 1_x_x'
        elif col == 'Label 2':
            rename_dict[merged_col] = 'Label 2_x_x'
        elif col == 'Label 3':
            rename_dict[merged_col] = 'Label 3_x_x'
        elif col == 'Label 4':
            rename_dict[merged_col] = 'Label 4_x_x'
        elif col == 'Label 5':
            rename_dict[merged_col] = 'Label 5_x_x'
        elif col == 'Note':
            rename_dict[merged_col] = 'Note_x'
        elif col == 'category':
            rename_dict[merged_col] = 'category_x'
        elif col == 'bid_id_header':
            rename_dict[merged_col] = 'bid_id_header_x'
        else:
            rename_dict[merged_col] = merged_col  # keep as is if no mapping

# For src1 columns (right), they have suffix _y added by pandas except join keys
for col in src1.columns:
    if col in ['sampled_bid_id', 'message_timestamp']:
        # sampled_bid_id is join key, message_timestamp is join key
        # sampled_bid_id not needed in target, will drop later
        continue
    else:
        merged_col = col + '_y'
        if col == 'message_sender':
            rename_dict[merged_col] = 'message_sender_y'
        elif col == 'message':
            rename_dict[merged_col] = 'message'
        elif col == 'category':
            rename_dict[merged_col] = 'category_y'
        elif col == 'agent_group':
            rename_dict[merged_col] = 'agent_group'
        else:
            rename_dict[merged_col] = merged_col  # keep as is if no mapping

merged = merged.rename(columns=rename_dict)

# Drop columns not in target schema
drop_cols = ['sampled_bid_id']
merged = merged.drop(columns=[c for c in drop_cols if c in merged.columns])

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

# Some columns may not exist in merged, so filter only existing columns
final_columns = [col for col in target_columns if col in merged.columns]

merged = merged[final_columns]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length9_70/target_multisource_mcts.csv", index=False)