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
    join_1 = ['Target1_1',   'Target1_2', 'Target1_5',
               'Target1_7', 'Target1_8',   'Target1_12',
               'Target1_14', 'Target1_15',
               'Target1_17',  'Target1_19', 'Target1_25',
               'Target1_26', 'Target1_28', 'Target1_30', 'Target1_31',
               'Target1_32', 'Target1_33', 'Target1_36',
               'Target1_37', 'Target1_39',  'Target1_42',
               'Target1_45',  'Target1_47',  'Target1_49',
               'Target1_50',  'Target1_51', 'Target1_56',  'Target1_58',
                 'Target1_63', 'Target1_64',
               'Target1_66', 'Target1_69',  'Target1_70', 'Target1_73',
               'Target1_74',  'Target1_76', 'Target1_79',
               'Target1_83', 'Target1_85',
              'Target1_94',  'Target1_96', 'Target1_98']
    join_2 = ['Target2_0', 'Target2_2', 'Target2_3', 'Target2_4', 'Target2_5',
              'Target2_6', 'Target2_7', 'Target2_8', 'Target2_9', 'Target2_10',
              'Target2_11', 'Target2_12', 'Target2_13', 'Target2_14', 'Target2_15',
              'Target2_16', 'Target2_17', 'Target2_18', 'Target2_20', 'Target2_21',
              'Target2_22', 'Target2_23', 'Target2_24', 'Target2_25', 'Target2_26',
              'Target2_27', 'Target2_28', 'Target2_29', 'Target2_30', 'Target2_31',
              'Target2_32', 'Target2_33', 'Target2_34', 'Target2_35', 'Target2_36',
              'Target2_37', 'Target2_38', 'Target2_39', 'Target2_40', 'Target2_41',
              'Target2_42', 'Target2_43', 'Target2_44', 'Target2_46', 'Target2_47',
              'Target2_48', 'Target2_49', 'Target2_50', 'Target2_51', 'Target2_52',
              'Target2_53', 'Target2_54', 'Target2_55', 'Target2_56', 'Target2_57',
              'Target2_58', 'Target2_59', 'Target2_60', 'Target2_62', 'Target2_63',
              'Target2_64', 'Target2_65', 'Target2_66', 'Target2_67', 'Target2_68',
              'Target2_69', 'Target2_70', 'Target2_71', 'Target2_72', 'Target2_73',
              'Target2_74', 'Target2_75', 'Target2_76', 'Target2_77', 'Target2_78',
              'Target2_79', 'Target2_81', 'Target2_82', 'Target2_84', 'Target2_85',
              'Target2_86', 'Target2_88', 'Target2_89', 'Target2_91', 'Target2_92',
              'Target2_93', 'Target2_95', 'Target2_96', 'Target2_97', 'Target2_98',
              'Target2_99']
    join_test = [
              'Target2_18', 'Target2_20', 'Target2_21',
              'Target2_22', 'Target2_23', 'Target2_24', 'Target2_25', 'Target2_26',
              'Target2_27', 'Target2_28', 'Target2_29', 'Target2_30', 'Target2_31',
              'Target2_32', 'Target2_33', 'Target2_34', 'Target2_35', 'Target2_36',
              'Target2_37', 'Target2_38', 'Target2_39', 'Target2_40', 'Target2_41',
              'Target2_42', 'Target2_43', 'Target2_44', 'Target2_46', 'Target2_47',
              'Target2_48', 'Target2_49', 'Target2_50', 'Target2_51', 'Target2_52',
              'Target2_53', 'Target2_54', 'Target2_55', 'Target2_56', 'Target2_57',
              'Target2_58', 'Target2_59', 'Target2_60', 'Target2_62', 'Target2_63',
              'Target2_64', 'Target2_65', 'Target2_66', 'Target2_67', 'Target2_68',
              'Target2_69', 'Target2_70', 'Target2_71', 'Target2_72', 'Target2_73',
              'Target2_74', 'Target2_75', 'Target2_76', 'Target2_77', 'Target2_78',
              'Target2_79', 'Target2_81', 'Target2_82', 'Target2_84', 'Target2_85',
              'Target2_86', 'Target2_88', 'Target2_89', 'Target2_91', 'Target2_92',
              'Target2_93', 'Target2_95', 'Target2_96', 'Target2_97', 'Target2_98',
              'Target2_99']
    cot_1 = ['Target1_0', 'Target1_3', 'Target1_4', 'Target1_6', 'Target1_10', 'Target1_11', 'Target1_13',
             'Target1_20', 'Target1_21', 'Target1_29', 'Target1_38', 'Target1_46', 'Target1_48',
             'Target1_57', 'Target1_59', 'Target1_60', 'Target1_61', 'Target1_65', 'Target1_67',
             'Target1_71', 'Target1_80'
             ]

    seen = set()
    filtered_ids = [x for x in filtered_ids if not (x in seen or seen.add(x))]
    print(len(filtered_ids))

    return ['Target1_8']
