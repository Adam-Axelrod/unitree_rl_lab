# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

RL environments for Unitree robots (Go2, Go2W, B2, H1, H1-2, G1-23dof, G1-29dof) built as an **Isaac Lab 2.3.0 / Isaac Sim 5.1.0** extension, plus a **C++ deployment stack** that runs the trained ONNX policies on MuJoCo (sim2sim) and real hardware (sim2real) over `unitree_sdk2` DDS.

Two halves that must stay in sync:
- `source/unitree_rl_lab/` — Python package (editable install) with the training envs.
- `deploy/` — C++ runtime that re-implements just enough of Isaac Lab's manager stack to replay a policy from a YAML config.

## Commands

All helper commands assume bash + an activated conda env that has Isaac Lab installed. The deploy side is **Linux-only** (ships `onnxruntime-linux-x64`, reads `/proc/self/exe`, needs DDS).

```bash
./unitree_rl_lab.sh -i                                    # editable install + conda activate.d hook + argcomplete
./unitree_rl_lab.sh -l                                    # list registered Unitree tasks (no Isaac Sim launch — fast)
./unitree_rl_lab.sh -t --task Unitree-G1-29dof-Velocity   # train (adds --headless); tab-completes task names
./unitree_rl_lab.sh -p --task Unitree-G1-29dof-Velocity   # play latest checkpoint + export policy.pt/.onnx

# equivalent direct invocations
python scripts/rsl_rl/train.py --headless --task <TASK> [--num_envs N] [--max_iterations N] [--resume --load_run <dir>] [--distributed] [--video]
python scripts/rsl_rl/play.py --task <TASK> [--num_envs N] [--checkpoint path] [--real-time]

# mimic (motion-tracking) preprocessing — required before training a mimic task
python scripts/mimic/csv_to_npz.py -f path/to/motion.bvh_60hz.csv --input_fps 60 [--frame_range S E] [--output_fps 50]
python scripts/mimic/replay_npz.py -f path/to/motion.npz

# lint (deploy/ and .vscode/ are excluded)
pre-commit run --all-files
```

Training logs land in `logs/rsl_rl/<experiment_name>/<timestamp>_<run_name>/`, where `experiment_name` defaults to the task id lowercased with `-`→`_` (see `scripts/rsl_rl/cli_args.py:57`). There is no test suite.

C++ controller build (per robot, Linux):

```bash
cd deploy/robots/g1_29dof && mkdir build && cd build && cmake .. && make   # -> ./g1_ctrl
./g1_ctrl --network eth0     # omit --network for MuJoCo sim2sim on domain 0
```

## Architecture

### Task registration and discovery

Tasks are gym-registered in leaf `__init__.py` files under `tasks/<family>/robots/<robot>/<variant>/`, e.g. [tasks/locomotion/robots/g1/29dof/__init__.py](source/unitree_rl_lab/unitree_rl_lab/tasks/locomotion/robots/g1/29dof/__init__.py). `tasks/__init__.py` recursively imports every subpackage via `isaaclab_tasks.utils.import_packages`, so **creating the directory + `gym.register` call is all that's needed** — no central registry to edit.

Every registration supplies three entry points:
- `env_cfg_entry_point` → `RobotEnvCfg` (training)
- `play_env_cfg_entry_point` → `RobotPlayEnvCfg` (fewer envs, wider command ranges) — resolved by the local [utils/parser_cfg.py](source/unitree_rl_lab/unitree_rl_lab/utils/parser_cfg.py), *not* Isaac Lab's `parse_env_cfg`
- `rsl_rl_cfg_entry_point` → the family's `BasePPORunnerCfg`

`scripts/list_envs.py` avoids launching Isaac Sim by walking `tasks/locomotion.robots` and `tasks/mimic.robots` directly; `train.py` imports it at module scope purely to populate the `--task` argcomplete choices before `AppLauncher` runs.

Script structure follows the Isaac Lab convention strictly: argparse → `AppLauncher(args)` → **then** all `isaaclab.*` imports. Adding an import above the launcher will break.

### Task families

- **`tasks/locomotion/`** — velocity-tracking. One `velocity_env_cfg.py` per robot; terrain generator, height scanner, contact sensors, curricula (`terrain_levels_vel`, `lin_vel_cmd_levels`), 5-step observation history.
- **`tasks/mimic/`** — motion tracking (whole-body). One directory per motion clip, each with a `tracking_env_cfg.py` and the source `.csv`. The env cfg points at a sibling `.npz` that is **gitignored and must be generated first** with `scripts/mimic/csv_to_npz.py` — that script replays the CSV through Isaac Sim to capture body-frame states, so the npz is robot-specific (currently G1-29dof only).

Each family has an `mdp/` package that star-imports Isaac Lab's mdp terms and then overrides/extends them (`from isaaclab.envs.mdp import *` followed by local `rewards`, `observations`, `commands`, …). Config files always reference terms as `mdp.<name>` so the local override wins.

### Robot assets — `assets/robots/unitree.py`

Central definition of every `UnitreeArticulationCfg`. Two things matter beyond the usual actuator gains:

1. **`UNITREE_MODEL_DIR` / `UNITREE_ROS_DIR` are placeholder paths** that must be edited locally before anything spawns. USD and URDF spawn cfgs coexist; the URDF variant is commented out per robot and `UnitreeUrdfFileCfg.replace_asset()` symlinks meshes into `/tmp` (Linux-only).
2. **`joint_sdk_names`** — ordered list mapping Isaac Lab's internal joint order to the robot's SDK motor indices. Empty strings mark unused motor slots. This list is what `export_deploy_cfg` turns into `joint_ids_map`, and it is the single point where a sim/hardware ordering mistake becomes a hardware failure.

`UNITREE_G1_29DOF_MIMIC_CFG` derives stiffness/damping from armature and a target natural frequency, and `UNITREE_G1_29DOF_MIMIC_ACTION_SCALE` derives per-joint action scales as `0.25 * effort_limit / stiffness` — changing actuator params silently changes the action space for mimic tasks.

### Sim → deploy contract (`deploy.yaml`)

This is the core cross-language interface.

- At **train** time, [utils/export_deploy_cfg.py](source/unitree_rl_lab/unitree_rl_lab/utils/export_deploy_cfg.py) writes `<log_dir>/params/deploy.yaml`: `joint_ids_map`, `step_dt`, resolved `stiffness`/`damping`/`default_joint_pos` in SDK order, the action term with numerically resolved `scale`/`offset`/`clip`, and every **policy-group** observation term with its resolved `scale`, `clip`, and `history_length`.
- At **play** time, `policy.pt` and `policy.onnx` are exported to `<log_dir>/exported/`.
- At **deploy** time, `deploy/include/isaaclab/` rebuilds an `ObservationManager` + `ActionManager` from that YAML and drives the ONNX policy in a thread ticking at `step_dt`.

Consequences to keep in mind:
- Every observation term name in `deploy.yaml` must have a matching C++ `REGISTER_OBSERVATION(<same_name>)` in [observations.h](deploy/include/isaaclab/envs/mdp/observations/observations.h) or per-robot `State_*.cpp`; otherwise the controller throws at startup. Adding a new Python observation term to a policy group means adding its C++ twin.
- Observation *order* in the YAML must match the training group order — it is the flattened policy input.
- Only the `policy` group is exported; `critic`/privileged terms are irrelevant to deployment.
- The checked-in `deploy/robots/*/config/policy/**/params/deploy.yaml` files are exported copies that have been hand-edited (e.g. the commented `keyboard_velocity_commands` alternative). Don't assume they are byte-identical to a fresh export.

### C++ deployment layout

- `deploy/include/` — shared, robot-agnostic: the Isaac Lab manager mirror (`isaaclab/`) and the FSM (`FSM/`).
- `deploy/robots/<robot>/` — `main.cpp`, `Types.h` (SDK message types), `src/State_*.cpp`, and `config/config.yaml`.

`config.yaml` is the control plane: the `FSM._` block lists enabled states (`id`, optional `type` selecting the C++ class via `REGISTER_FSM`), and each state block declares `transitions` as a joystick DSL expression (`LT + B.on_pressed`, `LT(2s) + down.on_pressed`) parsed at construction. A `Passive` fallback transition on `lowstate` timeout and a `bad_orientation` guard are registered for every state automatically. `policy_dir` may be relative to the executable's project dir; if it contains no `exported/` folder, `param::parser_policy_dir` picks the **newest sorted subdirectory that does** — which is why pointing it at `logs/rsl_rl/<experiment>` just works.

The FSM thread runs at 1 kHz (`pre_run` → `run` → `post_run` → transition checks) while the policy runs in its own thread at `step_dt` (50 Hz for the shipped configs).

## Conventions

- Formatting is enforced by pre-commit: black (`--line-length 120 --preview`), flake8 (+ simplify/return plugins), isort with a custom `ISAACLABPARTY` section (`isaaclab*` imports form their own group, above first-party `unitree_rl_lab`). `deploy/` is excluded — match the surrounding C++ style there by hand.
- No USD/`.npz`/`.pt` files in the repo (gitignored); motion CSVs and ONNX policies are tracked.
- Env cfg classes are always named `RobotSceneCfg` / `RobotEnvCfg` / `RobotPlayEnvCfg` regardless of robot, and the robot cfg is imported `as ROBOT_CFG`, so cfg files are near-copyable between robots.
