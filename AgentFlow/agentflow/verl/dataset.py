import json
import torch
from verl.utils.dataset.rl_dataset import RLHFDataset


class AgentDataset(RLHFDataset):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filter_overlong_prompts = False

    def __getitem__(self, item):
        row_dict: dict = self.dataframe[item]

        # Our DataMorpher parquet may store extra_info as a JSON string.
        extra_info = row_dict.get("extra_info", {})
        if isinstance(extra_info, str):
            try:
                extra_info = json.loads(extra_info)
            except Exception:
                extra_info = {}
        elif not isinstance(extra_info, dict):
            extra_info = {}
        row_dict["extra_info"] = extra_info

        # add index for each prompt
        index = extra_info.get("index", extra_info.get("idx", 0))
        row_dict["index"] = index
        # Workaround for data proto. At least one tensor is needed.
        row_dict["fake_ids"] = torch.ones(1, dtype=torch.int)
        return row_dict
