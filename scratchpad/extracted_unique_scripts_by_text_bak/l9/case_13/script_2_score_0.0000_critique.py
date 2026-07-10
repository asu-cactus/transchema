import pandas as pd

# Read all source tables with index_col=0 as per hint 22
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_13/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_9.csv",
]

dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Key columns to join on
key_cols = ['Date', 'Jour', 'Chaine']

# Start with the first dataframe
df_merged = dfs[0]

# Iteratively join all other dataframes on the key columns
for i in range(1, len(dfs)):
    df_merged = df_merged.merge(
        dfs[i],
        on=key_cols,
        how='inner',
        suffixes=('', f'_{i}')
    )

# The merge will add suffixes to overlapping columns except the keys.
# The target schema has suffixes like _x, _y, _x_37, _x_38, etc.
# We need to rename columns to exactly match the target schema.

# The target schema columns are given, and the order is important.
# We will reorder and rename columns to match the target schema exactly.

# Load target schema columns from the problem statement
target_columns = ['Date', 'Jour_x', 'Chaine_x', 'Heure_prgm1_x', 'Titre_prgm1_x', 'Type_prgm1_x', 'Duree_prgm1_x', 'Nbre_episodes_prgm1_x', 'Age_conseille_prgm1_x', 'Heure_prgm2_x', 'Titre_prgm2_x', 'Type_prgm2_x', 'Duree_prgm2_x', 'Nbre_episodes_prgm2_x', 'Age_conseille_prgm2_x', 'Part_de_marche_x', 'Annee_x', 'Mois_x', 'Week end_x',
                  'Jour_y', 'Chaine_y', 'Heure_prgm1_y', 'Titre_prgm1_y', 'Type_prgm1_y', 'Duree_prgm1_y', 'Nbre_episodes_prgm1_y', 'Age_conseille_prgm1_y', 'Heure_prgm2_y', 'Titre_prgm2_y', 'Type_prgm2_y', 'Duree_prgm2_y', 'Nbre_episodes_prgm2_y', 'Age_conseille_prgm2_y', 'Part_de_marche_y', 'Annee_y', 'Mois_y', 'Week end_y',
                  'Jour_x_37', 'Chaine_x_38', 'Heure_prgm1_x_39', 'Titre_prgm1_x_40', 'Type_prgm1_x_41', 'Duree_prgm1_x_42', 'Nbre_episodes_prgm1_x_43', 'Age_conseille_prgm1_x_44', 'Heure_prgm2_x_45', 'Titre_prgm2_x_46', 'Type_prgm2_x_47', 'Duree_prgm2_x_48', 'Nbre_episodes_prgm2_x_49', 'Age_conseille_prgm2_x_50', 'Part_de_marche_x_51', 'Annee_x_52', 'Mois_x_53', 'Week end_x_54',
                  'Jour_y_55', 'Chaine_y_56', 'Heure_prgm1_y_57', 'Titre_prgm1_y_58', 'Type_prgm1_y_59', 'Duree_prgm1_y_60', 'Nbre_episodes_prgm1_y_61', 'Age_conseille_prgm1_y_62', 'Heure_prgm2_y_63', 'Titre_prgm2_y_64', 'Type_prgm2_y_65', 'Duree_prgm2_y_66', 'Nbre_episodes_prgm2_y_67', 'Age_conseille_prgm2_y_68', 'Part_de_marche_y_69', 'Annee_y_70', 'Mois_y_71', 'Week end_y_72',
                  'Jour_x_73', 'Chaine_x_74', 'Heure_prgm1_x_75', 'Titre_prgm1_x_76', 'Type_prgm1_x_77', 'Duree_prgm1_x_78', 'Nbre_episodes_prgm1_x_79', 'Age_conseille_prgm1_x_80', 'Heure_prgm2_x_81', 'Titre_prgm2_x_82', 'Type_prgm2_x_83', 'Duree_prgm2_x_84', 'Nbre_episodes_prgm2_x_85', 'Age_conseille_prgm2_x_86', 'Part_de_marche_x_87', 'Annee_x_88', 'Mois_x_89', 'Week end_x_90',
                  'Jour_y_91', 'Chaine_y_92', 'Heure_prgm1_y_93', 'Titre_prgm1_y_94', 'Type_prgm1_y_95', 'Duree_prgm1_y_96', 'Nbre_episodes_prgm1_y_97', 'Age_conseille_prgm1_y_98', 'Heure_prgm2_y_99', 'Titre_prgm2_y_100', 'Type_prgm2_y_101', 'Duree_prgm2_y_102', 'Nbre_episodes_prgm2_y_103', 'Age_conseille_prgm2_y_104', 'Part_de_marche_y_105', 'Annee_y_106', 'Mois_y_107', 'Week end_y_108',
                  'Jour_x_109', 'Chaine_x_110', 'Heure_prgm1_x_111', 'Titre_prgm1_x_112', 'Type_prgm1_x_113', 'Duree_prgm1_x_114', 'Nbre_episodes_prgm1_x_115', 'Age_conseille_prgm1_x_116', 'Heure_prgm2_x_117', 'Titre_prgm2_x_118', 'Type_prgm2_x_119', 'Duree_prgm2_x_120', 'Nbre_episodes_prgm2_x_121', 'Age_conseille_prgm2_x_122', 'Part_de_marche_x_123', 'Annee_x_124', 'Mois_x_125', 'Week end_x_126',
                  'Jour_y_127', 'Chaine_y_128', 'Heure_prgm1_y_129', 'Titre_prgm1_y_130', 'Type_prgm1_y_131', 'Duree_prgm1_y_132', 'Nbre_episodes_prgm1_y_133', 'Age_conseille_prgm1_y_134', 'Heure_prgm2_y_135', 'Titre_prgm2_y_136', 'Type_prgm2_y_137', 'Duree_prgm2_y_138', 'Nbre_episodes_prgm2_y_139', 'Age_conseille_prgm2_y_140', 'Part_de_marche_y_141', 'Annee_y_142', 'Mois_y_143', 'Week end_y_144',
                  'Jour_x_145', 'Chaine_x_146', 'Heure_prgm1_x_147', 'Titre_prgm1_x_148', 'Type_prgm1_x_149', 'Duree_prgm1_x_150', 'Nbre_episodes_prgm1_x_151', 'Age_conseille_prgm1_x_152', 'Heure_prgm2_x_153', 'Titre_prgm2_x_154', 'Type_prgm2_x_155', 'Duree_prgm2_x_156', 'Nbre_episodes_prgm2_x_157', 'Age_conseille_prgm2_x_158', 'Part_de_marche_x_159', 'Annee_x_160', 'Mois_x_161', 'Week end_x_162',
                  'Jour_y_163', 'Chaine_y_164', 'Heure_prgm1_y_165', 'Titre_prgm1_y_166', 'Type_prgm1_y_167', 'Duree_prgm1_y_168', 'Nbre_episodes_prgm1_y_169', 'Age_conseille_prgm1_y_170', 'Heure_prgm2_y_171', 'Titre_prgm2_y_172', 'Type_prgm2_y_173', 'Duree_prgm2_y_174', 'Nbre_episodes_prgm2_y_175', 'Age_conseille_prgm2_y_176', 'Part_de_marche_y_177', 'Annee_y_178', 'Mois_y_179', 'Week end_y_180']

# The merged dataframe columns are:
# key_cols + for each source except first, columns with suffix _i
# We need to rename columns to match target columns exactly.

# Build a mapping from merged df columns to target columns:
# The first source columns keep original names (except keys)
# The second source columns have suffix _1, third _2, ..., ninth _8
# The tenth source columns have suffix _9

# The target columns have suffixes _x, _y, _x_37, _x_38, etc.
# The pattern is:
# Source0 columns: suffix _x
# Source1 columns: suffix _y
# Source2 columns: suffix _x_37, _x_38, ...
# Source3 columns: suffix _x_39, _x_40, ...
# and so on.

# We will map source index to suffix pattern:
# source 0: _x
# source 1: _y
# source 2: _x_37, _x_38, ...
# source 3: _x_39, _x_40, ...
# source 4: _x_42, _x_43, ...
# source 5: _x_44, _x_45, ...
# source 6: _x_46, _x_47, ...
# source 7: _x_48, _x_49, ...
# source 8: _x_50, _x_51, ...
# source 9: _x_52, _x_53, ...

# But the target columns show a complex pattern with _x, _y, _x_37, _x_38, etc.
# For simplicity, we will rename columns in the merged df to exactly the target columns in order.

# The merged df columns order:
# keys: Date, Jour, Chaine
# then source0 columns except keys
# then source1 columns except keys with suffix _1
# then source2 columns except keys with suffix _2
# ...
# then source9 columns except keys with suffix _9

# Let's build a list of columns for each source (excluding keys)
source_cols = dfs[0].columns.tolist()
source_cols_no_keys = [c for c in source_cols if c not in key_cols]

# For each source, get columns excluding keys
all_source_cols = []
for i, df in enumerate(dfs):
    cols = df.columns.tolist()
    cols_no_keys = [c for c in cols if c not in key_cols]
    all_source_cols.append(cols_no_keys)

# Build merged df columns list:
merged_cols = key_cols.copy()
for i in range(len(dfs)):
    if i == 0:
        merged_cols.extend(all_source_cols[0])
    else:
        merged_cols.extend([f"{c}_{i}" for c in all_source_cols[i]])

# Now map merged_cols to target_columns
# The length of merged_cols and target_columns should be equal
assert len(merged_cols) == len(target_columns), "Column count mismatch"

# Rename columns accordingly
df_merged.columns = merged_cols
df_merged = df_merged[target_columns]

# Save to CSV
df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length9_13/target_multisource_mcts.csv", index=False)