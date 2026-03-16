import os
from pathlib import Path

import hydra
import ray

from .dataset import AgentDataset
from .trainer import AgentFlowTrainer
from verl.trainer.ppo.reward import load_reward_manager
from verl.trainer.main_ppo import create_rl_sampler

# Marker written by the container build when flash-attn is compiled from source
# with sm_120 (Blackwell) CUDA kernel support.  See apptainer.def / Dockerfile.chpc.
_FLASH_ATTN_SM120_MARKER = Path("/etc/flash_attn_sm120_built")


def _should_use_flash_attn_shim() -> bool:
    """Return True when the SDPA compatibility shim must be active for Ray workers.

    Background
    ----------
    PyPI flash_attn wheels contain CUDA kernels compiled only for sm<=90.
    Calling them on a Blackwell GPU (sm_120) produces an unhandled CUDA error
    that kills the worker process without a Python traceback.

    The AgentFlow/train/flash_attn_shim package provides SDPA-backed
    (torch.nn.functional.scaled_dot_product_attention) drop-in replacements
    for all flash_attn symbols imported by HuggingFace transformers and verl.
    SDPA is mathematically equivalent to flash attention and natively compiled
    for all GPU architectures, including Blackwell.

    Decision logic
    --------------
    1. If the current GPU is pre-Blackwell (sm < 120): PyPI wheels work → no shim.
    2. If the GPU is Blackwell+ (sm >= 120) AND the container was built with the
       native flash_attn source build (marker file present): the installed wheel
       has sm_120 kernels → no shim.
    3. Otherwise (Blackwell+ without native build): activate the shim.

    The marker file /etc/flash_attn_sm120_built is written by the container build
    script only when `pip install flash-attn` from source succeeds with
    TORCH_CUDA_ARCH_LIST=12.0+PTX.  Once the container is rebuilt the shim
    becomes a no-op automatically.
    """
    try:
        import torch
        if not torch.cuda.is_available():
            return False
        major, minor = torch.cuda.get_device_capability()
        sm = major * 10 + minor          # e.g. 12*10+0 = 120 for Blackwell
        if sm < 120:
            return False                 # pre-Blackwell: standard wheels work
        if _FLASH_ATTN_SM120_MARKER.exists():
            return False                 # native sm_120 kernels present in container
        return True                      # Blackwell + no native build → need shim
    except Exception:
        return False                     # can't determine; assume no shim needed


@hydra.main(config_path="pkg://agentflow/verl", config_name="config", version_base=None)
def main(config):
    run_ppo(config)


def run_ppo(config) -> None:
    if not ray.is_initialized():
        # Forward all AGENTFLOW_* env vars into the Ray runtime so they are
        # visible inside every Ray actor (TaskRunner, WorkerDict, etc.).
        # Without this, vars set in the launcher process after `ray start --head`
        # may not be inherited by actors spawned by the existing head daemon.
        agentflow_env_vars = {
            k: v for k, v in os.environ.items() if k.startswith("AGENTFLOW_")
        }

        runtime_env_vars: dict = {
            "TOKENIZERS_PARALLELISM": "true",
            "NCCL_DEBUG": "WARN",
            "VLLM_LOGGING_LEVEL": "WARN",
            **agentflow_env_vars,
        }

        if _should_use_flash_attn_shim():
            # Prepend the SDPA-backed flash_attn compatibility shim to PYTHONPATH
            # so every Ray actor uses it in place of the system flash_attn package.
            # The shim is self-deactivating: _should_use_flash_attn_shim() returns
            # False once the container is rebuilt with native sm_120 kernels.
            shim_dir = str(
                Path(__file__).parent.parent.parent  # AgentFlow/
                / "train" / "flash_attn_shim"
            )
            existing = os.environ.get("PYTHONPATH", "")
            runtime_env_vars["PYTHONPATH"] = (
                f"{shim_dir}:{existing}" if existing else shim_dir
            )
            print(
                f"[entrypoint] GPU sm_120 detected without native flash_attn build.\n"
                f"  Activating SDPA compatibility shim: {shim_dir}\n"
                f"  Attention computation is mathematically equivalent to flash_attn.\n"
                f"  To use native kernels: rebuild the container (see apptainer.def)."
            )

        ray.init(
            runtime_env={"env_vars": runtime_env_vars},
            num_cpus=config.ray_init.num_cpus,
        )

    runner = TaskRunner.remote()
    ray.get(runner.run.remote(config))


@ray.remote(num_cpus=1)  # please make sure main_task is not scheduled on head
class TaskRunner:
    def run(self, config):
        # print initial config
        from pprint import pprint

        from omegaconf import OmegaConf

        from verl.utils.fs import copy_to_local

        pprint(OmegaConf.to_container(config, resolve=True))  # resolve=True will eval symbol values
        OmegaConf.resolve(config)

        # download the checkpoint from hdfs
        local_path = copy_to_local(config.actor_rollout_ref.model.path)

        # instantiate tokenizer
        from verl.utils import hf_processor, hf_tokenizer

        trust_remote_code = config.data.get("trust_remote_code", False)
        tokenizer = hf_tokenizer(local_path, trust_remote_code=trust_remote_code)
        processor = hf_processor(local_path, use_fast=True)  # used for multimodal LLM, could be none

        # define worker classes
        if config.actor_rollout_ref.actor.strategy in ["fsdp", "fsdp2"]:
            assert config.critic.strategy in ["fsdp", "fsdp2"]
            from verl.single_controller.ray import RayWorkerGroup
            from verl.workers.fsdp_workers import ActorRolloutRefWorker, AsyncActorRolloutRefWorker, CriticWorker

            actor_rollout_cls = (
                AsyncActorRolloutRefWorker
                if config.actor_rollout_ref.rollout.mode == "async"
                else ActorRolloutRefWorker
            )
            ray_worker_group_cls = RayWorkerGroup

        elif config.actor_rollout_ref.actor.strategy == "megatron":
            assert config.actor_rollout_ref.actor.strategy == config.critic.strategy
            from verl.single_controller.ray.megatron import NVMegatronRayWorkerGroup
            from verl.workers.megatron_workers import ActorRolloutRefWorker, CriticWorker

            actor_rollout_cls = ActorRolloutRefWorker
            ray_worker_group_cls = NVMegatronRayWorkerGroup

        else:
            raise NotImplementedError

        from verl.trainer.ppo.ray_trainer import ResourcePoolManager, Role

        role_worker_mapping = {
            Role.ActorRollout: ray.remote(actor_rollout_cls),
            Role.Critic: ray.remote(CriticWorker),
        }

        global_pool_id = "global_pool"
        resource_pool_spec = {
            global_pool_id: [config.trainer.n_gpus_per_node] * config.trainer.nnodes,
        }
        mapping = {
            Role.ActorRollout: global_pool_id,
            Role.Critic: global_pool_id,
        }

        # we should adopt a multi-source reward function here
        # - for rule-based rm, we directly call a reward score
        # - for model-based rm, we call a model
        # - for code related prompt, we send to a sandbox if there are test cases
        # - finally, we combine all the rewards together
        # - The reward type depends on the tag of the data
        if config.reward_model.enable:
            if config.reward_model.strategy in ["fsdp", "fsdp2"]:
                from verl.workers.fsdp_workers import RewardModelWorker
            elif config.reward_model.strategy == "megatron":
                from verl.workers.megatron_workers import RewardModelWorker
            else:
                raise NotImplementedError
            role_worker_mapping[Role.RewardModel] = ray.remote(RewardModelWorker)
            mapping[Role.RewardModel] = global_pool_id

        # use reference model
        if config.algorithm.use_kl_in_reward or config.actor_rollout_ref.actor.use_kl_loss:
            role_worker_mapping[Role.RefPolicy] = ray.remote(ActorRolloutRefWorker)
            mapping[Role.RefPolicy] = global_pool_id

        reward_fn = load_reward_manager(
            config, tokenizer, num_examine=0, **config.reward_model.get("reward_kwargs", {})
        )
        val_reward_fn = load_reward_manager(
            config, tokenizer, num_examine=1, **config.reward_model.get("reward_kwargs", {})
        )
        resource_pool_manager = ResourcePoolManager(resource_pool_spec=resource_pool_spec, mapping=mapping)

        from verl.utils.dataset.rl_dataset import collate_fn

        # Use our special dataset
        train_dataset = AgentDataset(
            data_files=config.data.train_files,
            tokenizer=tokenizer,
            processor=processor,
            config=config.data,
        )
        val_dataset = AgentDataset(
            data_files=config.data.val_files,
            tokenizer=tokenizer,
            processor=processor,
            config=config.data,
        )
        train_sampler = create_rl_sampler(config.data, train_dataset)
        trainer = AgentFlowTrainer(
            config=config,
            tokenizer=tokenizer,
            processor=processor,
            role_worker_mapping=role_worker_mapping,
            resource_pool_manager=resource_pool_manager,
            ray_worker_group_cls=ray_worker_group_cls,
            reward_fn=reward_fn,
            val_reward_fn=val_reward_fn,
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            collate_fn=collate_fn,
            train_sampler=train_sampler,
        )
        trainer.init_workers()
        trainer.fit()


if __name__ == "__main__":
    main()
