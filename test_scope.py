import json


def get_test_cases_ids(json_file_path, len_id, max_len_id, target_id, max_target_id):
    # Read the JSON file
    with open(json_file_path, 'r') as file:
        data_list = json.load(file)

    # Find the item with the specified Source Data Name
    ids = [item["Target Data Name"] for item in data_list]

    # Adjust the filter criteria
    filtered_ids = []
    for id in ids:
        parts = id[6:].split('_')
        if len(parts) >= 2:
            len_part = int(parts[0])
            target_part = int(parts[1])
            if len_id <= len_part <= max_len_id and target_id <= target_part <= max_target_id:
                filtered_ids.append(id)

    # bad_ids = ['Target1_16']
    past_at_least_once = ['Target1_0', 'Target1_3', 'Target1_4', 'Target1_6', 'Target1_11', 'Target1_20',
                          'Target1_21', 'Target1_29', 'Target1_34', 'Target1_35', 'Target1_38',
                          'Target1_55', 'Target1_60', 'Target1_65', 'Target1_67', 'Target1_71',
                          'Target1_72', 'Target1_80', 'Target1_84']
    finish_issue = ['Target1_27', 'Target1_46', 'Target1_97']  # 27, 46, 97
    further_finish_issue = ['Target1_97']
    with_dirty_rows = ['Target1_40', 'Target1_59']
    with_similarity_issue = ['Target1_10']  # , 'Target1_23', 'Target1_62', 'Target1_86', 'Target1_97']
    with_syntax_issue = ['Target1_44', 'Target1_78', 'Target1_88', 'Target1_89', 'Target1_90', 'Target1_91',
                         'Target1_92', 'Target1_93']

    print('Total number of test cases:', len(filtered_ids))
    # print('Number of bad test cases:', len(bad_ids))
    # filtered_ids = [id for id in filtered_ids if id not in bad_ids]
    # filtered_ids = [id for id in filtered_ids if id not in past_at_least_once]
    baseline_5_iters = [
        "Target1_6", "Target1_9", "Target1_13", "Target1_16", "Target1_18", "Target1_22",
        "Target1_23", "Target1_24", "Target1_27", "Target1_34", "Target1_35", "Target1_38",
        "Target1_40", "Target1_41", "Target1_43", "Target1_44", "Target1_46", "Target1_52",
        "Target1_54", "Target1_55", "Target1_57", "Target1_68", "Target1_72", "Target1_75",
        "Target1_78", "Target1_80", "Target1_81", "Target1_84", "Target1_86", "Target1_87",
        "Target1_88", "Target1_89", "Target1_90", "Target1_91", "Target1_93", "Target1_95",
        "Target1_97", "Target1_99"
    ]
    baseline_5_iters_2nd = [
        'Target1_6', 'Target1_35', 'Target1_40', 'Target1_57', 'Target1_72', 'Target1_84',
        'Target1_88', 'Target1_91', 'Target1_93']
    baseline_5_iters_3rd = [
        'Target1_72', 'Target1_84', 'Target1_91', 'Target1_93']
    baseline_5_iters_4th = ['Target1_55', 'Target1_72', 'Target1_88']

    cot_1 = ['Target1_0', 'Target1_3', 'Target1_4', 'Target1_6', 'Target1_10', 'Target1_11', 'Target1_13',
             'Target1_20', 'Target1_21', 'Target1_29', 'Target1_38', 'Target1_46', 'Target1_48',
             'Target1_57', 'Target1_59', 'Target1_60', 'Target1_61', 'Target1_65', 'Target1_67',
             'Target1_71', 'Target1_80'
             ]
    #filtered_ids = [id for id in filtered_ids if (id not in cot_1 and int(id.split('_')[1]) > 86)]
    target_array = [
        'Target1_22',
        'Target1_24',
        # 'Target1_34',
        # 'Target1_40',
        # 'Target1_43',
        # 'Target1_44',
        # 'Target1_52',
        'Target1_54',
        # 'Target1_55',
        'Target1_72',
        # 'Target1_75',
        # 'Target1_77',
        # 'Target1_84',
        'Target1_87',
        # 'Target1_89',
        'Target1_90',
        'Target1_91',
        'Target1_93'
    ]

    print('Number of Test cases after filtering:', len(target_array))
    return filtered_ids#['Target1_90']
