import json
import os
import gymnasium as gym
import numpy as np
import re
import string
from collections import Counter
#from react.quality import *

DATA_DIR = "../data"

class HistoryWrapper(gym.ObservationWrapper):
    def __init__(self, env, obs_format, prompt=None):
        super().__init__(env)
        assert obs_format in ["obs", "history"]
        if obs_format == "history":
            assert hasattr(self.env, "traj")
        self.obs_format = obs_format
        self.prompt = prompt if prompt is not None else ""

    def observation(self, obs):
        if self.obs_format == "obs":
            return obs
        elif self.obs_format == "history":
            observation = self.env.traj["observations"][0] + "\n"
            for i, (o, a) in enumerate(zip(self.env.traj["observations"][1:], self.env.traj["actions"]), 1):
                observation += f"Action {i}: {a}\nObservation {i}: {o}\n\n"
            return self.prompt + observation



class TransWrapper(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)
        self.data = []
        self.data_idx = 0

    def reset(self, seed=None, return_info=False, options=None, idx=None):
        self.env.reset(seed=seed, return_info=return_info, options=options)
        try:
            self.env.step('')
        except:
            pass
        self.env.reset(seed=seed, return_info=return_info, options=options)
        self.data_idx = int(np.random.randint(len(self.data))) if idx is None else idx
        observation = f"Question: {self.data[self.data_idx][0]}"
        info = self._get_info()
        return (observation, info) if return_info else observation

    def _get_info(self):
        return {
            "steps": self.steps,
            "answer": self.answer,
            "question": self.data[self.data_idx][0],
            "hotpot_split": self.split
        }

    def get_reward(self, info):
        #if info['answer'] is not None:
        #    pred = normalize_answer(self.data[self.data_idx][1])
        #    gt = normalize_answer(info['answer'])
        #    score = (pred == gt)
        #    return int(score)
        return 0


    def step(self, action, num_generate_sample):
        # TODO: first step obs does not have question.
        obs, _, done, info = self.env.step(action, num_generate_sample)
        reward = self.get_reward(info)
        if done:
            obs = f"Episode finished, reward = {reward}\n"
            info.update({"gt_answer": self.data[self.data_idx][1], "question_idx": self.data_idx})
            info.update(self.get_metrics(info))
        return obs, reward, done, info

    def __len__(self):
        return len(self.data)



class LoggingWrapper(gym.Wrapper):
    def __init__(self, env, folder="trajs", file_id=None):
        super().__init__(env)
        self.trajs = []
        self.traj = {"observations": [], "actions": []}
        self.folder = folder
        self.file_id = np.random.randint(0, 10000000) if file_id is None else file_id
        self.file_path = f"{self.folder}/{self.file_id}.json"
        os.makedirs("../trajs", exist_ok=True)
    def __len__(self):
        return len(self.env.data)

    def reset(self, seed=None, return_info=False, options=None, idx=None):
        output = self.env.reset(seed=seed, return_info=return_info, options=options, idx=idx)
        observation = output[0] if return_info else output
        self.traj = {"observations": [observation], "actions": []}
        return output

    def step(self, action, num_generate_sample):
        obs, reward, done, info = self.env.step(action, num_generate_sample)
        self.traj["observations"].append(obs)
        self.traj["actions"].append(action)
        if done:
            self.traj.update(info)
        return obs, reward, done, info

    def update_record(self):
        if len(self.traj) > 0:
            self.trajs.append(self.traj)
            self.traj = {"observations": [], "actions": []}

    def write(self):
        self.update_record()
        with open(self.file_path, "w") as f:
            json.dump(self.trajs, f)
            print(f"Saved trajs to trajs/{self.file_id}.json")

    def close(self):
        self.write()
