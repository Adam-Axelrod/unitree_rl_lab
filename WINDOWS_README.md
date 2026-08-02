# Unitree RL Lab (Windows)

[![IsaacSim](https://img.shields.io/badge/IsaacSim-5.1.0-silver.svg)](https://docs.omniverse.nvidia.com/isaacsim/latest/overview.html)
[![Isaac Lab](https://img.shields.io/badge/IsaacLab-2.3.0-silver)](https://isaac-sim.github.io/IsaacLab)
[![License](https://img.shields.io/badge/license-Apache2.0-yellow.svg)](https://opensource.org/license/apache-2-0)
[![Discord](https://img.shields.io/badge/-Discord-5865F2?style=flat&logo=Discord&logoColor=white)](https://discord.gg/ZwcVwxv5rq)

> Windows counterpart of [README.md](README.md). Same steps, but every command is PowerShell and
> `unitree_rl_lab.sh` is never used — that script resolves `${CONDA_PREFIX}/bin/python`, which does
> not exist in a Windows conda env, and installs a `activate.d/setenv.sh` hook that PowerShell
> activation never runs. Run everything below from an **Anaconda PowerShell Prompt** (or any
> PowerShell where `conda activate` works).

## Overview

This project provides a set of reinforcement learning environments for Unitree robots, built on top of [IsaacLab](https://github.com/isaac-sim/IsaacLab).

Currently supports Unitree **Go2**, **H1** and **G1-29dof** robots.

<div align="center">

| <div align="center"> Isaac Lab </div> | <div align="center">  Mujoco </div> |  <div align="center"> Physical </div> |
|--- | --- | --- |
| [<img src="https://oss-global-cdn.unitree.com/static/d879adac250648c587d3681e90658b49_480x397.gif" width="240px">](g1_sim.gif) | [<img src="https://oss-global-cdn.unitree.com/static/3c88e045ab124c3ab9c761a99cb5e71f_480x397.gif" width="240px">](g1_mujoco.gif) | [<img src="https://oss-global-cdn.unitree.com/static/6c17c6cf52ec4e26bbfab1fbf591adb2_480x270.gif" width="240px">](g1_real.gif) |

</div>

## Installation

- Install Isaac Lab by following the [installation guide](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/pip_installation.html). On Windows the pip route is the supported one:

  ```powershell
  conda create -n env_isaaclab python=3.11 -y
  conda activate env_isaaclab

  python -m pip install --upgrade pip
  pip install torch==2.7.0 torchvision --index-url https://download.pytorch.org/whl/cu128
  pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com

  git clone https://github.com/isaac-sim/IsaacLab.git C:\Users\aa24\PhD\IsaacLab
  cd C:\Users\aa24\PhD\IsaacLab
  .\isaaclab.bat --install          # NOT ./isaaclab.sh
  ```

- Install the Unitree RL IsaacLab standalone environments.

  - Clone or copy this repository separately from the Isaac Lab installation (i.e. outside the `IsaacLab` directory):

    ```powershell
    git clone https://github.com/unitreerobotics/unitree_rl_lab.git
    ```
  - Use a python interpreter that has Isaac Lab installed, install the library in editable mode using:

    ```powershell
    conda activate env_isaaclab
    cd C:\Users\aa24\PhD\unitree_rl_lab
    git lfs install
    pip install -e source\unitree_rl_lab
    ```

    > This replaces `./unitree_rl_lab.sh -i`. The `pip install -e` above is the only part of that
    > script that does real work on Windows; the conda `activate.d` hook and
    > `activate-global-python-argcomplete` are bash-only and are intentionally skipped. No shell
    > restart is required.

- Download unitree robot description files

  *Method 1: Using USD Files [Use this one on Windows]*
  - Download unitree usd files from [unitree_model](https://huggingface.co/datasets/unitreerobotics/unitree_model/tree/main), keeping folder structure
    ```powershell
    git clone https://huggingface.co/datasets/unitreerobotics/unitree_model C:\Users\aa24\PhD\unitree_model
    ```
  - Config `UNITREE_MODEL_DIR` in `source\unitree_rl_lab\unitree_rl_lab\assets\robots\unitree.py`.

    ```python
    UNITREE_MODEL_DIR = "C:/Users/aa24/PhD/unitree_model"
    ```

    > Use forward slashes (or escaped backslashes) — this string is interpolated straight into
    > `usd_path=f"{UNITREE_MODEL_DIR}/G1/29dof/usd/..."`, so a raw `C:\Users\...` would produce
    > invalid escape sequences.

  *Method 2: Using URDF Files* — **not supported on Windows.**
  - `UnitreeUrdfFileCfg.replace_asset()` hardcodes `/tmp/IsaacLab/unitree_rl_lab` and calls
    `os.symlink` (`assets/robots/unitree.py:81-90`). There is no `/tmp` on Windows, and symlink
    creation additionally requires Developer Mode or an elevated shell. Leave `UNITREE_ROS_DIR`
    unset and leave every `robot_cfg.spawn` on its USD variant. Use Method 1 instead.

- Verify that the environments are correctly installed by:

  - Listing the available tasks:

    ```powershell
    python scripts\list_envs.py     # replaces ./unitree_rl_lab.sh -l ; does not launch Isaac Sim
    ```

    Expected output is a table of 5 tasks: `Unitree-G1-29dof-Velocity`, `Unitree-Go2-Velocity`,
    `Unitree-H1-Velocity`, `Unitree-G1-29dof-Mimic-Dance-102`,
    `Unitree-G1-29dof-Mimic-Gangnanm-Style`.

  - Running a task:

    ```powershell
    python scripts\rsl_rl\train.py --headless --task Unitree-G1-29dof-Velocity
    ```

    > Replaces `./unitree_rl_lab.sh -t --task ...`. **You must type `--headless` yourself** — the
    > shell wrapper added it silently. Task-name tab completion is bash-only, so type task names in
    > full. Optional flags are unchanged: `--num_envs N`, `--max_iterations N`,
    > `--resume --load_run <dir>`, `--video`.

  - Inference with a trained agent:

    ```powershell
    python scripts\rsl_rl\play.py --task Unitree-G1-29dof-Velocity
    ```

    > Replaces `./unitree_rl_lab.sh -p --task ...`. Exports `policy.pt` and `policy.onnx` to
    > `logs\rsl_rl\<experiment_name>\<run>\exported\`. Add `--real-time` to run at wall-clock speed.

  If `python` ever resolves to the wrong interpreter, call this machine's env directly:
  `& "C:\Users\aa24\AppData\Local\miniconda3\envs\env_isaaclab\python.exe" scripts\list_envs.py`

## Deploy

After the model training is completed, we need to perform sim2sim on the trained strategy in Mujoco to test the performance of the model.
Then deploy sim2real.

**The `deploy/` stack cannot be built on Windows.** It ships `onnxruntime-linux-x64`, reads
`/proc/self/exe`, and needs `unitree_sdk2` DDS. Run this half inside **WSL2** — train on Windows,
deploy from WSL2. Install it once from PowerShell:

```powershell
wsl --install -d Ubuntu-22.04
```

All commands in this section run **inside the WSL2 Ubuntu shell**, not PowerShell.

### Setup

```bash
# Install dependencies
sudo apt update
sudo apt install -y build-essential cmake git libyaml-cpp-dev libboost-all-dev libeigen3-dev libspdlog-dev libfmt-dev
# Install unitree_sdk2
git clone https://github.com/unitreerobotics/unitree_sdk2.git ~/unitree_sdk2
cd ~/unitree_sdk2
mkdir build && cd build
cmake .. -DBUILD_EXAMPLES=OFF # Install on the /usr/local directory
sudo make install
# Clone this repo inside the WSL filesystem — building on /mnt/c is slow and breaks CMake symlinks
git clone https://github.com/unitreerobotics/unitree_rl_lab.git ~/unitree_rl_lab
# Compile the robot_controller
cd ~/unitree_rl_lab/deploy/robots/g1_29dof # or other robots
mkdir build && cd build
cmake .. && make
```

Copy the policy trained on Windows into the WSL clone before running the controller — the Windows
drive is mounted at `/mnt/c`:

```bash
cp -r /mnt/c/Users/aa24/PhD/unitree_rl_lab/logs/rsl_rl/unitree_g1_29dof_velocity \
      ~/unitree_rl_lab/logs/rsl_rl/
```

Point `policy_dir` in `deploy/robots/g1_29dof/config/config.yaml` at that directory. It may be
relative to the executable's project dir, and if it contains no `exported/` folder the loader picks
the newest sorted subdirectory that does — so naming it `logs/rsl_rl/<experiment>` just works.

### Sim2Sim

Installing the [unitree_mujoco](https://github.com/unitreerobotics/unitree_mujoco?tab=readme-ov-file#installation) inside WSL2. The MuJoCo viewer renders through WSLg, which is available on Windows 11 — no X server setup needed.

- Set the `robot` at `/simulate/config.yaml` to g1
- Set `domain_id` to 0
- Set `enable_elastic_hand` to 1
- Set `use_joystck` to 1.

```bash
# start simulation
cd ~/unitree_mujoco/simulate/build
./unitree_mujoco
# ./unitree_mujoco -i 0 -n lo -r g1 -s scene_29dof.xml # alternative
```

```bash
cd ~/unitree_rl_lab/deploy/robots/g1_29dof/build
./g1_ctrl
# 1. press [L2 + Up] to set the robot to stand up
# 2. Click the mujoco window, and then press 8 to make the robot feet touch the ground.
# 3. Press [R1 + X] to run the policy.
# 4. Click the mujoco window, and then press 9 to disable the elastic band.
```

Both processes must run in the same WSL2 instance so they share the loopback DDS domain.

### Sim2Real

You can use this program to control the robot directly, but make sure the on-borad control program has been closed.

WSL2's default NAT networking blocks the DDS multicast the robot needs. Enable mirrored networking
first — create `C:\Users\aa24\.wslconfig` in Windows:

```ini
[wsl2]
networkingMode=mirrored
```

then `wsl --shutdown` from PowerShell and reopen the WSL shell. Pass the **Windows** adapter name
connected to the robot (find it with `ipconfig`; `ip a` inside WSL will mirror it):

```bash
./g1_ctrl --network eth0 # eth0 is the network interface name.
```

> If mirrored networking is unavailable or the robot still does not appear, run the controller from
> a native Linux machine on the robot's network. Sim2real over WSL2 is not a configuration Unitree
> tests against.

## Acknowledgements

This repository is built upon the support and contributions of the following open-source projects. Special thanks to:

- [IsaacLab](https://github.com/isaac-sim/IsaacLab): The foundation for training and running codes.
- [mujoco](https://github.com/google-deepmind/mujoco.git): Providing powerful simulation functionalities.
- [robot_lab](https://github.com/fan-ziqi/robot_lab): Referenced for project structure and parts of the implementation.
- [whole_body_tracking](https://github.com/HybridRobotics/whole_body_tracking): Versatile humanoid control framework for motion tracking.
