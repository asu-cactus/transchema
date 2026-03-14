"""
Launch script for DataMorpher RL fine-tuning.

Usage:
  # From the AgentFlow/ directory:
  python train/train_datamorpheragent.py

  # With per-run overrides (passed through to agentflow.verl as Hydra args):
  python train/train_datamorpheragent.py trainer.total_epochs=10 data.train_batch_size=32

Steps performed:
  1. (Optional) Prepare training data if parquet files don't exist yet.
  2. Set environment variables from datamorpherconfig.yaml.
  3. Start the rollout server  (python train/datamorpherrollout.py)  in a background process.
  4. Launch the verl PPO/GRPO trainer  (python -m agentflow.verl).
"""

import os
import sys
import yaml
import time
import signal
import argparse
import subprocess
import importlib.util
from pathlib import Path
import json


CONFIG_FILE = "train/datamorpherconfig.yaml"
ROLLOUT_SCRIPT = "train/datamorpherrollout.py"
DATA_PREP_SCRIPT = "train/prepare_rl_data.py"
AGENTFLOW_ROOT = Path(__file__).resolve().parents[1]


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        config = yaml.safe_load(f)
    if config is None:
        raise ValueError(f"Empty or invalid YAML: {config_path}")
    return config


def _resolve_path(path_str: str) -> str:
    """Resolve relative paths against AgentFlow root for Ray worker safety."""
    expanded = os.path.expandvars(path_str)
    p = Path(expanded)
    if p.is_absolute():
        return str(p)
    return str((AGENTFLOW_ROOT / p).resolve())


def set_env_vars(env_section: dict):
    print("Setting environment variables...")
    for key, value in env_section.items():
        os.environ[key] = str(value)
        print(f"  {key}={value}")

    # Normalize path-like env vars to absolute paths (Ray workers may run elsewhere).
    for path_key in ("BASE_DATA_DIR", "CHECKPOINT_DIR", "ROLLOUT_DIR", "HF_HOME"):
        val = os.environ.get(path_key)
        if val:
            abs_val = _resolve_path(val)
            os.environ[path_key] = abs_val
            print(f"  {path_key}={abs_val}")
            Path(abs_val).mkdir(parents=True, exist_ok=True)

    # Ensure HuggingFace cache exists even if not provided in YAML.
    if "HF_HOME" not in os.environ:
        hf_cache = _resolve_path("/scratch/general/vast/u1592362/hf_cache")
        os.environ["HF_HOME"] = hf_cache
        Path(hf_cache).mkdir(parents=True, exist_ok=True)
        print(f"  HF_HOME={hf_cache}")

    # vLLM 0.9.x + this AgentFlow async path expects V1 engine mode.
    # Explicitly set to avoid Ray worker env drift.
    os.environ["VLLM_USE_V1"] = "1"
    print("  VLLM_USE_V1=1")
    # vLLM CuMem allocator is incompatible with expandable_segments:True.
    # Keep allocator config conservative and vLLM-safe.
    alloc_conf = os.environ.get("PYTORCH_CUDA_ALLOC_CONF", "")
    if "expandable_segments:True" in alloc_conf:
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
        print(
            "  Replaced incompatible PYTORCH_CUDA_ALLOC_CONF "
            f"'{alloc_conf}' -> '{os.environ['PYTORCH_CUDA_ALLOC_CONF']}'"
        )
    elif not alloc_conf:
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
        print(f"  PYTORCH_CUDA_ALLOC_CONF={os.environ['PYTORCH_CUDA_ALLOC_CONF']}")
    else:
        print(f"  PYTORCH_CUDA_ALLOC_CONF={alloc_conf}")

    # ------------------------------------------------------------------ #
    # CHPC/ROCm compatibility:
    # veRL raises if ROCR_VISIBLE_DEVICES is set together with
    # CUDA_VISIBLE_DEVICES or HIP_VISIBLE_DEVICES.
    # ------------------------------------------------------------------ #
    cuda_set = bool(os.environ.get("CUDA_VISIBLE_DEVICES"))
    hip_set = bool(os.environ.get("HIP_VISIBLE_DEVICES"))
    rocr_set = "ROCR_VISIBLE_DEVICES" in os.environ
    if (cuda_set or hip_set) and rocr_set:
        removed = os.environ.pop("ROCR_VISIBLE_DEVICES", None)
        print(
            "  Removed ROCR_VISIBLE_DEVICES because CUDA/HIP visibility is set "
            f"(old value: {removed})"
        )

    print(
        "  GPU env => "
        f"CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')} "
        f"HIP_VISIBLE_DEVICES={os.environ.get('HIP_VISIBLE_DEVICES')} "
        f"ROCR_VISIBLE_DEVICES={os.environ.get('ROCR_VISIBLE_DEVICES')}"
    )

    # Single-node single-GPU: rollout server and proxy are on the same machine; use
    # 127.0.0.1 for the proxy so the rollout process can always connect (node IP may
    # be unreachable from same host on some clusters).
    n_gpus = int(os.environ.get("N_GPUS", "1"))
    if n_gpus == 1:
        os.environ["AGENTFLOW_USE_LOCALHOST_PROXY"] = "1"
        print("  AGENTFLOW_USE_LOCALHOST_PROXY=1 (single-GPU)")


def maybe_prepare_data(config: dict):
    """
    Run prepare_rl_data.py if the parquet files don't exist yet.
    Reads BASE_DATA_DIR from config env to resolve the expected paths.
    """
    base_data_dir = os.environ.get(
        "BASE_DATA_DIR",
        _resolve_path(config.get("env", {}).get("BASE_DATA_DIR", "train/data")),
    )
    train_parquet = os.path.join(base_data_dir, "train", "datamorphertrain.parquet")
    val_parquet = os.path.join(base_data_dir, "val", "datamorpherval.parquet")

    if os.path.exists(train_parquet) and os.path.exists(val_parquet):
        print(f"Parquet files already exist — skipping data preparation.")
        print(f"  train: {train_parquet}")
        print(f"  val:   {val_parquet}")
        return

    print("Parquet files not found. Running prepare_rl_data.py ...")
    result = subprocess.run(
        [
            sys.executable,
            DATA_PREP_SCRIPT,
            "--output_train", train_parquet,
            "--output_val", val_parquet,
        ],
        check=True,
        env=os.environ,
        cwd=str(AGENTFLOW_ROOT),
    )
    if result.returncode != 0:
        print("ERROR: Data preparation failed.")
        sys.exit(result.returncode)
    print("Data preparation complete.")


def build_verl_command(python_args: dict, overrides: list) -> list:
    command = [sys.executable, "-m", "agentflow.verl"]
    for key, value in python_args.items():
        if isinstance(value, str):
            expanded = os.path.expandvars(value)
            command.append(f"{key}={expanded}")
        else:
            command.append(f"{key}={value}")
    command.extend(overrides)
    return command


def _expand_cfg_value(value: str) -> str:
    """Expand env vars in config values like ${BASE_DATA_DIR}/..."""
    return os.path.expandvars(value)


def _default_smoke_overrides() -> list[str]:
    """
    Tiny run to surface runtime errors quickly.
    Keeps GRPO wiring intact but minimizes workload.
    """
    return [
        "data.train_batch_size=1",
        "actor_rollout_ref.rollout.n=1",
        "actor_rollout_ref.actor.ppo_mini_batch_size=1",
        "actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=1",
        "actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=1",
        "actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=1",
        "actor_rollout_ref.actor.use_kl_loss=False",
        "actor_rollout_ref.actor.kl_loss_coef=0.0",
        "algorithm.use_kl_in_reward=False",
        # veRL sets vLLM max_model_len = max_prompt_length + max_response_length.
        # Qwen2.5-7B supports 128K; the limit comes from this config, not the model.
        # 12288 + 1024 = 13312.  use_remove_padding=True keeps training fast.
        "data.max_prompt_length=12288",
        "data.max_response_length=1024",
        "actor_rollout_ref.rollout.gpu_memory_utilization=0.25",
        "actor_rollout_ref.actor.fsdp_config.optimizer_offload=True",
        "trainer.total_epochs=1",
        "trainer.critic_warmup=999999",
        "trainer.save_freq=999999",
        "trainer.test_freq=999999",
        "trainer.val_before_train=False",
        "trainer.logger=['console']",
    ]


def _parse_extra_info(extra_info: object) -> dict:
    if isinstance(extra_info, dict):
        return extra_info
    if isinstance(extra_info, str):
        try:
            parsed = json.loads(extra_info)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def run_preflight_checks(config: dict):
    """
    Fast deterministic checks before launching rollout/training.
    Catches common failures in seconds.
    """
    print("\nRunning preflight checks ...")

    # 1) Verify parquet paths resolve and exist
    py_args = config.get("python_args", {})
    train_file = _expand_cfg_value(str(py_args.get("data.train_files", "")))
    val_file = _expand_cfg_value(str(py_args.get("data.val_files", "")))
    if not train_file or not val_file:
        raise RuntimeError("Missing data.train_files or data.val_files in config.")
    if not os.path.exists(train_file):
        raise FileNotFoundError(f"Train parquet not found: {train_file}")
    if not os.path.exists(val_file):
        raise FileNotFoundError(f"Val parquet not found: {val_file}")
    print(f"  OK parquet paths:\n    train={train_file}\n    val={val_file}")

    # 2) Load one example via datasets API (same path as verl)
    try:
        import datasets  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"Failed to import datasets: {exc}") from exc

    train_ds = datasets.load_dataset("parquet", data_files=train_file)["train"]
    val_ds = datasets.load_dataset("parquet", data_files=val_file)["train"]
    if len(train_ds) == 0 or len(val_ds) == 0:
        raise RuntimeError(
            f"Empty dataset detected: train={len(train_ds)} val={len(val_ds)}"
        )
    print(f"  OK dataset sizes: train={len(train_ds)} val={len(val_ds)}")

    row = train_ds[0]
    question = str(row.get("question", "")).strip()
    if not question:
        raise RuntimeError("First train row has empty 'question'.")

    # 3) Validate extra_info payload + referenced CSV files
    extra_info = _parse_extra_info(row.get("extra_info", {}))
    test_csv_paths = extra_info.get("test_csv_paths", [])
    target_csv_path = extra_info.get("target_csv_path")
    if not isinstance(test_csv_paths, list) or not test_csv_paths:
        raise RuntimeError(
            "extra_info.test_csv_paths missing/empty in first train row."
        )
    if not target_csv_path:
        raise RuntimeError("extra_info.target_csv_path missing in first train row.")
    missing = [p for p in test_csv_paths if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError(f"Missing test CSV paths: {missing[:3]}")
    if not os.path.exists(target_csv_path):
        raise FileNotFoundError(f"Missing target CSV path: {target_csv_path}")
    print("  OK sample task payload and referenced CSV files.")

    # 4) flash-attn is optional on CHPC. The environment follows the patched
    # transformers/no-flash-attn path, so don't hard-fail here.
    print("  Skipping flash-attn preflight (optional on this CHPC path).")

    print("Preflight checks passed.")


def restart_ray_if_available():
    """
    Restart local Ray so workers inherit the sanitized env from this launcher.
    This avoids stale env vars from previously started Ray daemons.
    """
    print("\nRefreshing Ray runtime environment ...")
    subprocess.run(
        ["ray", "stop", "--force"],
        check=False,
        env=os.environ,
        cwd=str(AGENTFLOW_ROOT),
    )
    start = subprocess.run(
        ["ray", "start", "--head"],
        check=False,
        env=os.environ,
        cwd=str(AGENTFLOW_ROOT),
        capture_output=True,
        text=True,
    )
    if start.returncode != 0:
        print("[WARN] ray start --head failed; continuing and letting Ray auto-init.")
        print(start.stderr[-500:])
    else:
        print("Ray restarted successfully.")


def ensure_runtime_dependencies(auto_install: bool = True):
    """
    Preflight-check runtime deps that otherwise fail deep inside Ray workers.
    """
    def _can_import_flash_attn() -> tuple[bool, str]:
        if importlib.util.find_spec("flash_attn") is None:
            return False, "not installed"
        try:
            importlib.import_module("flash_attn")
            return True, ""
        except Exception as exc:
            return False, str(exc)

    ok, err = _can_import_flash_attn()
    if ok:
        print("Runtime dependency check: flash-attn OK")
    else:
        print(f"flash-attn not usable ({err}); continuing without it.")
    return


def main():
    parser = argparse.ArgumentParser(
        description="Launch DataMorpher RL fine-tuning (rollout server + verl trainer)."
    )
    parser.add_argument(
        "--config",
        default=CONFIG_FILE,
        help=f"Path to config YAML (default: {CONFIG_FILE})",
    )
    parser.add_argument(
        "--skip_data_prep",
        action="store_true",
        help="Skip automatic data preparation even if parquet files are missing.",
    )
    parser.add_argument(
        "--skip_dep_check",
        action="store_true",
        help="Skip runtime dependency preflight (flash-attn check/install).",
    )
    parser.add_argument(
        "--preflight_only",
        action="store_true",
        help="Run fast preflight checks and exit.",
    )
    parser.add_argument(
        "--smoke_test",
        action="store_true",
        help="Run a tiny 1-epoch smoke training to fail fast.",
    )
    # Any remaining args are forwarded to agentflow.verl as Hydra overrides
    args, overrides = parser.parse_known_args()

    # ------------------------------------------------------------------ #
    # 1. Load config
    # ------------------------------------------------------------------ #
    print(f"\n{'='*60}")
    print(f"  DataMorpher RL Fine-Tuning")
    print(f"  Config: {args.config}")
    print(f"{'='*60}\n")

    config = load_config(args.config)

    # ------------------------------------------------------------------ #
    # 2. Set environment variables
    # ------------------------------------------------------------------ #
    set_env_vars(config.get("env", {}))
    restart_ray_if_available()
    if not args.skip_dep_check:
        ensure_runtime_dependencies(auto_install=True)

    # ------------------------------------------------------------------ #
    # 3. Prepare data (if needed)
    # ------------------------------------------------------------------ #
    if not args.skip_data_prep:
        maybe_prepare_data(config)

    # ------------------------------------------------------------------ #
    # 3b. Fast preflight checks
    # ------------------------------------------------------------------ #
    run_preflight_checks(config)
    if args.preflight_only:
        print("\nPreflight-only mode complete.")
        return

    # ------------------------------------------------------------------ #
    # 4. Start rollout server in background
    # ------------------------------------------------------------------ #
    agentflow_port = config.get("python_args", {}).get("agentflow.port", 9999)
    print(f"\nStarting DataMorpher rollout server on port {agentflow_port} ...")
    rollout_proc = subprocess.Popen(
        [sys.executable, ROLLOUT_SCRIPT],
        env=os.environ,
        cwd=str(AGENTFLOW_ROOT),
    )
    print(f"  Rollout server PID: {rollout_proc.pid}")

    # Give the rollout server a moment to bind its port before the trainer connects
    time.sleep(5)

    # ------------------------------------------------------------------ #
    # 5. Launch verl trainer
    # ------------------------------------------------------------------ #
    effective_overrides = list(overrides)
    if args.smoke_test:
        os.environ["AGENTFLOW_SMOKE_MODE"] = "1"
        os.environ["AGENTFLOW_SMOKE_SKIP_ACTOR_UPDATE"] = "1"
        os.environ.setdefault("AGENTFLOW_SMOKE_MAX_STEPS", "1")
        os.environ.setdefault("AGENTFLOW_SMOKE_WALLTIME_MIN", "25")
        print("  AGENTFLOW_SMOKE_MODE=1")
        print("  AGENTFLOW_SMOKE_SKIP_ACTOR_UPDATE=1")
        print(f"  AGENTFLOW_SMOKE_MAX_STEPS={os.environ['AGENTFLOW_SMOKE_MAX_STEPS']}")
        print(f"  AGENTFLOW_SMOKE_WALLTIME_MIN={os.environ['AGENTFLOW_SMOKE_WALLTIME_MIN']}")
        present_keys = {ov.split("=", 1)[0] for ov in effective_overrides if "=" in ov}
        for ov in _default_smoke_overrides():
            key = ov.split("=", 1)[0]
            if key not in present_keys:
                effective_overrides.append(ov)
        print("\nSmoke-test mode enabled (tiny run overrides applied).")

    command = build_verl_command(config.get("python_args", {}), effective_overrides)

    print(f"\nLaunching verl trainer:")
    print("  " + " ".join(str(c) for c in command))
    print("-" * 60)

    trainer_proc = None
    try:
        timeout_sec = None
        if args.smoke_test:
            try:
                walltime_min = int(os.environ.get("AGENTFLOW_SMOKE_WALLTIME_MIN", "20"))
                if walltime_min > 0:
                    timeout_sec = walltime_min * 60
            except ValueError:
                timeout_sec = 20 * 60
        trainer_proc = subprocess.run(
            command,
            check=True,
            env=os.environ,
            cwd=str(AGENTFLOW_ROOT),
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired:
        print(
            f"\nERROR: smoke test exceeded wall-clock limit "
            f"({os.environ.get('AGENTFLOW_SMOKE_WALLTIME_MIN', '20')} minutes)."
        )
        sys.exit(124)
    except subprocess.CalledProcessError as exc:
        print(f"\nERROR: verl trainer exited with code {exc.returncode}")
        sys.exit(exc.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        # Cleanly terminate the rollout server
        if rollout_proc and rollout_proc.poll() is None:
            print(f"\nShutting down rollout server (PID {rollout_proc.pid}) ...")
            rollout_proc.send_signal(signal.SIGTERM)
            try:
                rollout_proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                rollout_proc.kill()
            print("Rollout server stopped.")

    print("\nTraining complete.")


if __name__ == "__main__":
    main()
