"""Train the G1 (29 dof) velocity-tracking policy.

Launch with the VS Code play button (or F5) with `env_isaaclab` selected as the interpreter.
Edit CONFIG rather than passing arguments -- this file is the record of how the run was set up.

Logs land in logs/rsl_rl/unitree_g1_29dof_velocity/<timestamp>[_<run_name>]/.
"""

from _launcher import train

CONFIG = {
    "task": "Unitree-G1-29dof-Velocity",
    "headless": False,  # True hides the Isaac Sim viewport, which trains much faster
    "num_envs": 64,  # None keeps the value in the env cfg (also 4096)
    "max_iterations": 3000,  # None keeps BasePPORunnerCfg's 50000, i.e. "until you stop it"
    "seed": None,  # -1 samples a random seed
    "run_name": None,  # suffix appended to the log directory name
    "video": False,  # records to <log_dir>/videos/train, forces cameras on
    "logger": None,  # "tensorboard" | "wandb" | "neptune"
    # resuming: set resume=True and point load_run at a directory under the experiment folder
    "resume": False,
    "load_run": None,  # e.g. "2026-08-02_21-33-35"
    "checkpoint": None,  # e.g. "model_100.pt"
}

# Hydra overrides, applied on top of the env/agent cfg. Use these for scalar tweaks that
# do not need a code change -- they are dumped into <log_dir>/params/env.yaml with the run.
#
#   "env.rewards.track_lin_vel_xy.weight=2.0"
#   "env.rewards.feet_slide.weight=-0.2"
#   "agent.algorithm.entropy_coef=0.005"
#
# For anything structural (a new reward function, dropping a term) register a task variant
# instead; see experiments/README.md.
OVERRIDES = []

if __name__ == "__main__":
    train(CONFIG, OVERRIDES)
