"""Run inference on a trained G1 (29 dof) velocity policy.

Launch with the VS Code play button (or F5) with `env_isaaclab` selected as the interpreter.
Also exports policy.pt and policy.onnx into <log_dir>/exported/ for the C++ deploy stack.

Requires a trained run: this reads logs/rsl_rl/unitree_g1_29dof_velocity/, which only exists
after train_g1_29dof_velocity.py has been run. The policy.onnx shipped under
deploy/robots/g1_29dof/config/policy/velocity/ cannot be loaded here -- play.py rebuilds an
rsl_rl runner, so it needs a model_*.pt.
"""

from _launcher import play

CONFIG = {
    "task": "Unitree-G1-29dof-Velocity",
    "headless": False,  # you almost always want the viewport here
    "num_envs": 32,  # None keeps RobotPlayEnvCfg's 32
    "real_time": True,  # throttle to wall clock instead of running as fast as possible
    "video": False,  # records to <log_dir>/videos/play
    # which checkpoint to load -- leave both None for "latest run, latest model"
    "load_run": None,  # e.g. "2026-08-02_21-33-35"
    "checkpoint": None,  # a full path to a .pt, which overrides load_run entirely
}

if __name__ == "__main__":
    play(CONFIG)
