# experiments/

One script per run configuration, launched with the VS Code play button. Each is a `CONFIG`
dict plus a call into [_launcher.py](_launcher.py), which forwards to `scripts/rsl_rl/train.py`
or `scripts/rsl_rl/play.py` in this same process.

Requires `env_isaaclab` selected as the VS Code interpreter. Don't set
`python.terminal.executeInFileDir` — these scripts rely on the play button's default working
directory being the workspace root.

| script | what it does |
| --- | --- |
| `train_go2_velocity.py` | trains `Unitree-Go2-Velocity` |
| `train_go2_velocity_default.py` | trains `Unitree-Go2-Velocity` with stock settings (4096 envs, headless, no overrides) |
| `train_g1_29dof_velocity.py` | trains `Unitree-G1-29dof-Velocity` |
| `play_go2_velocity.py` | inference + ONNX export for the latest Go2 checkpoint |
| `play_g1_29dof_velocity.py` | inference + ONNX export for the latest G1 checkpoint |

## Testing different reward functions

Pick the cheapest option that expresses the change.

**1. Retuning a weight → `OVERRIDES` in the run script.**

```python
OVERRIDES = [
    "env.rewards.feet_slide.weight=-0.2",
    "env.rewards.track_lin_vel_xy.weight=2.0",
]
```

Hydra dotted paths, resolved against the env cfg. No code change, and the resolved value is
dumped into `<log_dir>/params/env.yaml`, so the run records what it actually trained with.
Pair it with `"run_name": "slide_0p2"` so the log directory is self-describing.

**2. A reward term that doesn't exist yet → add it to the family's `mdp/rewards.py`.**

`tasks/locomotion/mdp/` star-imports Isaac Lab's mdp terms and then overrides them, and every
cfg refers to terms as `mdp.<name>`, so a function added there is immediately referenceable.
Nothing else needs to change to make it available.

**3. Changing the *set* of terms → register a task variant.**

Hydra can retune a weight but cannot add or remove a term. Since task registration is
decentralized (see CLAUDE.md), a variant is cheap: subclass the env cfg, set terms to `None`
to drop them, and `gym.register` a new id next to the original.

```python
@configclass
class RobotEnvCfgNoAirTime(RobotEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.rewards.feet_air_time = None
        self.rewards.gait_symmetry = RewTerm(func=mdp.gait_symmetry, weight=0.5)
```

Register it as e.g. `Unitree-Go2-Velocity-Gait` and add a `train_go2_velocity_gait.py` here.
The new id derives its own `experiment_name` (`unitree_go2_velocity_gait`), so its logs and
checkpoints stay in a separate folder and the matching play script finds them automatically —
which is the real reason to prefer a variant over editing the base cfg in place.

Reward changes never affect the sim→deploy contract. Only observation and action terms feed
`deploy.yaml`; if you add an observation to the policy group, it needs a C++ twin (CLAUDE.md).
