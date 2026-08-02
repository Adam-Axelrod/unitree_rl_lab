"""Run inference on a trained Go2 velocity policy.

Launch with the VS Code play button (or F5) with `env_isaaclab` selected as the interpreter.
Also exports policy.pt and policy.onnx into <log_dir>/exported/ for the C++ deploy stack.

With checkpoint=None this picks the newest run under logs/rsl_rl/unitree_go2_velocity/ and
its highest-numbered model_*.pt. Pin `load_run` (and `checkpoint`) to evaluate a specific run.
"""

from _launcher import play

CONFIG = {
    "task": "Unitree-Go2-Velocity",
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
