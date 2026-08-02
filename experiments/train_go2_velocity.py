"""Train the Go2 velocity-tracking policy.

Launch with the VS Code play button (or F5) with `env_isaaclab` selected as the interpreter.
Edit CONFIG rather than passing arguments -- this file is the record of how the run was set up.

Logs land in logs/rsl_rl/unitree_go2_velocity/<timestamp>[_<run_name>]/.
"""

from _launcher import train

CONFIG = {
    "task": "Unitree-Go2-Velocity",
    "headless": False,  # True hides the Isaac Sim viewport, which trains much faster
    "num_envs": 64,  # None keeps the value in the env cfg (also 4096)
    "max_iterations": 1500,  # None keeps BasePPORunnerCfg's 50000, i.e. "until you stop it"
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
OVERRIDES = [
    # Chase env 0's robot instead of staring at the world origin from (7.5, 7.5, 7.5).
    # With origin_type=asset_root, eye/lookat are offsets from the robot's root and
    # Isaac Lab re-applies them every render step -- so mouse navigation gets overwritten.
    # Set origin_type back to "world" (or drop these) to steer the viewport by hand.
    # (viewer.asset_name="robot" is set in the Go2 env cfg -- Hydra cannot override a None field.)
    "env.viewer.origin_type=asset_root",
    "env.viewer.env_index=0",
    "env.viewer.eye=[2.0,2.0,1.0]",
    "env.viewer.lookat=[0.0,0.0,0.0]",
]

if __name__ == "__main__":
    train(CONFIG, OVERRIDES)
