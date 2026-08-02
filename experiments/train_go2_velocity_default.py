"""Train the Go2 velocity-tracking policy with the repo's stock settings.

The baseline run: no Hydra overrides, and every CONFIG knob left at None so the values in
the env cfg and BasePPORunnerCfg apply as shipped -- 4096 envs, 50000 iterations. This is
what `./unitree_rl_lab.sh -t --task Unitree-Go2-Velocity` does on Linux. Use it as the
reference to compare tuned runs against; copy it and edit rather than editing it in place.

Launch with the VS Code play button (or F5) with `env_isaaclab` selected as the interpreter.

Logs land in logs/rsl_rl/unitree_go2_velocity/<timestamp>_default/.
"""

from _launcher import train

CONFIG = {
    "task": "Unitree-Go2-Velocity",
    "headless": True,  # 4096 envs with a viewport open is not worth watching
    "num_envs": None,  # None keeps the env cfg's 4096
    "max_iterations": None,  # None keeps BasePPORunnerCfg's 50000, i.e. "until you stop it"
    "seed": None,  # -1 samples a random seed
    "run_name": "default",  # only labels the log directory; drop it for a bare timestamp
    "video": False,  # records to <log_dir>/videos/train, forces cameras on
    "logger": None,  # "tensorboard" | "wandb" | "neptune"
    # resuming: set resume=True and point load_run at a directory under the experiment folder
    "resume": False,
    "load_run": None,  # e.g. "2026-08-02_21-33-35"
    "checkpoint": None,  # e.g. "model_100.pt"
}

# Deliberately empty -- that is the point of this script. Tweaks belong in a copy of it.
OVERRIDES = []

if __name__ == "__main__":
    train(CONFIG, OVERRIDES)
