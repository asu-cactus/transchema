from quality.quality import analyze_functional_dependencies
from valentine import valentine_match, algorithms


def extract_dependencies(fd_dict):
    dependencies = set()  # Use a set to avoid duplicates
    for determinant, dependents in fd_dict.items():
        for dependent in dependents:
            dependencies.add((determinant, dependent))
    return dependencies


def get_filtered_functional_dependency(df):
    # Sample up to 1000 rows and use only first 15 columns because it becomes unfeasible beyond this and majority of keys are covered in first 15 columns
    df = df.sample(n=min(1000, df.shape[0]), replace=False)
    df = df.iloc[:, :15]

    # Analyze functional dependencies
    filtered_F, all_keys_sorted = analyze_functional_dependencies(df)

    if not filtered_F or not all_keys_sorted:
        return [], {}

    # Count how many times each key appears as determinant
    key_dependencies = {}
    for key_tuple, value in filtered_F:
        key = tuple(key_tuple) if isinstance(key_tuple, (list, tuple)) else (key_tuple,)
        if key not in key_dependencies:
            key_dependencies[key] = set()
        key_dependencies[key].add(value)

    # Sort keys by number of dependencies, descending
    sorted_keys = sorted(
        key_dependencies.keys(), key=lambda k: len(key_dependencies[k]), reverse=True
    )

    # Optional: Filter keys for presentation (e.g., if first column or if all key columns are string or first)
    sorted_filtered_keys = []
    for key in sorted_keys:
        # Check if any column in key is first column or is string
        if any(
            df.columns.get_loc(col) == 0 or df[col].dtype == "object" for col in key
        ):
            sorted_filtered_keys.append(key)

    # Build FD map from all keys (no filtering of FDs)
    filtered_fd = {key: key_dependencies[key] for key in sorted_keys}

    return sorted_filtered_keys, filtered_fd


def calculate_score(gt_df, tgt_df):

    # parameters
    w1 = 1
    w2 = 1
    w3 = 1
    p = 1

    # Match Functional Dependencies
    key_gt, fd_gt = get_filtered_functional_dependency(gt_df)
    key_tgt, fd_tgt = get_filtered_functional_dependency(tgt_df)

    print("\n\n\nScore Calculation\n\n\n")

    print(fd_gt)
    print(key_gt)
    print("\n\nTarget : ")
    print(fd_tgt)
    print(key_tgt)

    dependencies_gt = extract_dependencies(fd_gt)
    dependencies_tgt = extract_dependencies(fd_tgt)

    overlapping_dependencies = dependencies_gt.intersection(dependencies_tgt)
    overlapping_keys = set(key_gt).intersection(key_tgt)

    score_fd = (
        len(overlapping_dependencies) / len(dependencies_gt)
        if (len(dependencies_gt) > 0)
        else 1
    )
    score_key = len(overlapping_keys) / len(key_gt) if (len(key_gt) > 0) else 1

    matcher = algorithms.Cupid()

    # Match schemas
    matches = valentine_match(gt_df, tgt_df, matcher)
    gt_df_columns = gt_df.columns

    gt_df_columns = set(gt_df.columns)
    matched_columns = set(match[0] for match in matches)
    # print("\n\n Matchings : ", matches)

    column_mapping_score = len(matched_columns) / len(gt_df_columns)

    score = pow(
        w1 * (score_fd**p) + w2 * (score_key**p) + w3 * (column_mapping_score) ** p,
        1 / p,
    )

    print([score_fd, score_key, column_mapping_score])
    return score
