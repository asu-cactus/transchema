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
        return

    print(f"flash-attn not usable: {err}")
    if not auto_install:
        raise RuntimeError(
            "flash-attn is required by verl but is unavailable.\n"
            "Install manually in rl_env:\n"
            "  python -m pip install flash-attn --no-build-isolation --no-binary flash-attn\n"
        )

    # If a broken wheel is installed (e.g., GLIBC mismatch), remove it first.
    if "GLIBC_" in err or "cannot open shared object file" in err:
        print("Detected binary incompatibility in flash-attn; uninstalling broken wheel ...")
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", "flash-attn"],
            env=os.environ,
            cwd=str(AGENTFLOW_ROOT),
            check=False,
        )

    # Build/install in current environment. --no-binary helps avoid incompatible prebuilt wheels.
    print("Attempting flash-attn installation from source-compatible path ...")
    install_cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "flash-attn",
        "--no-build-isolation",
        "--no-binary",
        "flash-attn",
    ]
    result = subprocess.run(
        install_cmd,
        env=os.environ,
        cwd=str(AGENTFLOW_ROOT),
        check=False,
        text=True,
    )
    ok, err = _can_import_flash_attn()
    if result.returncode != 0 or not ok:
        raise RuntimeError(
            "Failed to install usable flash-attn.\n"
            "Current error: "
            f"{err}\n\n"
            "On CHPC, load CUDA toolchain modules and retry, e.g.:\n"
            "  module load cuda\n"
            "  python -m pip install flash-attn --no-build-isolation --no-binary flash-attn\n"
            "If cluster GLIBC/toolchain blocks this build, use a newer node/container."
        )
    print("flash-attn installed and importable.")


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
    command = build_verl_command(config.get("python_args", {}), overrides)

    print(f"\nLaunching verl trainer:")
    print("  " + " ".join(str(c) for c in command))
    print("-" * 60)

    trainer_proc = None
    try:
        trainer_proc = subprocess.run(
            command, check=True, env=os.environ, cwd=str(AGENTFLOW_ROOT)
        )
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
